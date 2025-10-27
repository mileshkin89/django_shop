from pathlib import Path
import polars as pl
from tqdm import tqdm
from typing import Dict, Iterable, List, Tuple

from django.db import transaction
from django.utils.text import slugify
from seed_data.catalog.description import get_random_description

from seed_data.catalog.dto import (
    MasterCategoryDTO,
    SubCategoryDTO,
    ArticleTypeDTO,
    BaseColourDTO,
    SeasonDTO,
    UsageTypeDTO,
    ProductDTO,
    ImageDTO,
    CatalogResultDTO,
)
from apps.catalog.models import (
    MasterCategory,
    SubCategory,
    ArticleType,
    BaseColour,
    Season,
    UsageType,
    Product,
)


class ProductGenerator:
    def __init__(
            self,
            products_path,
            images_path,
            batch_size = 1000
    ):
        self.products_path: Path = products_path
        self.images_path: Path = images_path
        self.batch_size: int = batch_size


    def seed_catalog(self):
        product_df, images_df = self._extract_csv()

        product_dto = self._transform(product_df, images_df)

        self._load(product_dto)


    def _drop_none(self, df):
        df = df.with_columns([
            pl.when(pl.col(c).str.strip_chars().eq(""))
            .then(None)
            .otherwise(pl.col(c))
            .alias(c)
            for c in df.columns
        ])
        df = df.drop_nulls().filter(~pl.any_horizontal(pl.all().is_in([""])))
        return df

    def _extract_csv(self):
        product_df = pl.read_csv(
            self.products_path,
            infer_schema_length=0,
            dtypes=[pl.Utf8],
            null_values=["", "NaN", "null"],
        )
        product_df = self._drop_none(product_df)
        product_df = product_df.with_columns([
            pl.col("product_id").cast(pl.Int64),
            pl.col("year").cast(pl.Int64),
        ])

        images_df = pl.read_csv(
            self.images_path,
            infer_schema_length = 0,
            dtypes=[pl.Utf8],
            null_values = ["", "NaN", "null"],
        )
        images_df = self._drop_none(images_df)

        return product_df, images_df

    def _transform(self, product_df: pl.DataFrame, images_df: pl.DataFrame) -> CatalogResultDTO:
        """Normalize data and build DTO collections using Polars."""

        master_categories = [
            MasterCategoryDTO(name=name)
            for name in product_df["master_category"]
            .drop_nulls()
            .unique()
            .sort()
            .to_list()
        ]

        sub_categories = [
            SubCategoryDTO(master_category=row["master_category"], name=row["sub_category"])
            for row in (
                product_df.select(["master_category", "sub_category"])
                .drop_nulls()
                .unique()
                .iter_rows(named=True)
            )
        ]

        article_types = [
            ArticleTypeDTO(sub_category=row["sub_category"], name=row["article_type"])
            for row in (
                product_df.select(["sub_category", "article_type"])
                .drop_nulls()
                .unique()
                .iter_rows(named=True)
            )
        ]

        base_colours = [
            BaseColourDTO(name=name)
            for name in product_df["base_colour"]
            .drop_nulls()
            .unique()
            .sort()
            .to_list()
        ]

        seasons = [
            SeasonDTO(name=name)
            for name in product_df["season"]
            .drop_nulls()
            .unique()
            .sort()
            .to_list()
        ]

        usage_types = [
            UsageTypeDTO(name=name)
            for name in product_df["usage"]
            .drop_nulls()
            .unique()
            .sort()
            .to_list()
        ]

        products = []
        for row in product_df.iter_rows(named=True):
            products.append(
                ProductDTO(
                    product_id=int(row["product_id"]),
                    gender=str(row["gender"]),
                    year=int(row["year"]),
                    product_display_name=str(row["product_display_name"]),
                    description=str(get_random_description()),
                    article_type=str(row["article_type"]),
                    base_colour=str(row["base_colour"]),
                    season=str(row["season"]),
                    usage=str(row["usage"]),
                )
            )

        images_df = images_df.with_columns([
            pl.col("filename")
            .str.split(".")
            .list.first()
            .cast(pl.Int64)
            .alias("product_id")
        ])

        images = [
            ImageDTO(product_id=int(row["product_id"]), image_url=str(row["link"]))
            for row in (
                images_df.select(["product_id", "link"])
                .drop_nulls()
                .iter_rows(named=True)
            )
        ]

        return CatalogResultDTO(
            master_categories=master_categories,
            sub_categories=sub_categories,
            article_types=article_types,
            base_colours=base_colours,
            seasons=seasons,
            usage_types=usage_types,
            products=products,
            images=images,
        )



    def _load(self, dto: CatalogResultDTO) -> None:
        with transaction.atomic():
            master_map = self._load_master_categories(dto.master_categories)
            sub_map = self._load_sub_categories(dto.sub_categories, master_map)
            article_type_map = self._load_article_types(dto.article_types, sub_map)
            base_colour_map = self._load_base_colours(dto.base_colours)
            season_map = self._load_seasons(dto.seasons)
            usage_type_map = self._load_usage_types(dto.usage_types)
            images_map = self._build_images_map(dto.images)
            self._load_products(
                dto.products,
                article_type_map,
                base_colour_map,
                season_map,
                usage_type_map,
                images_map,
            )

    def _load_master_categories(
            self, items: Iterable[MasterCategoryDTO]
    ) -> Dict[str, MasterCategory]:
        instances = [MasterCategory(name=i.name) for i in items]
        MasterCategory.objects.bulk_create(
            instances, batch_size=self.batch_size, ignore_conflicts=True
        )

        names = [i.name for i in items]
        qs = MasterCategory.objects.filter(name__in=names)
        return {obj.name: obj for obj in qs}

    def _load_sub_categories(
            self,
            items: Iterable[SubCategoryDTO],
            master_map: Dict[str, MasterCategory],
    ) -> Dict[str, SubCategory]:
        to_create: List[SubCategory] = []
        for dto in items:
            master = master_map.get(dto.master_category)
            if not master:
                continue
            to_create.append(SubCategory(master_category=master, name=dto.name))

        SubCategory.objects.bulk_create(
            to_create, batch_size=self.batch_size, ignore_conflicts=True
        )

        names = list({i.name for i in items})
        qs = SubCategory.objects.filter(name__in=names)
        return {obj.name: obj for obj in qs}

    def _load_article_types(
            self,
            items: Iterable[ArticleTypeDTO],
            sub_map: Dict[str, SubCategory],
    ) -> Dict[str, ArticleType]:
        to_create: List[ArticleType] = []
        for dto in items:
            sub = sub_map.get(dto.sub_category)
            if not sub:
                continue
            to_create.append(ArticleType(sub_category=sub, name=dto.name))

        ArticleType.objects.bulk_create(
            to_create, batch_size=self.batch_size, ignore_conflicts=True
        )

        names = list({i.name for i in items})
        qs = ArticleType.objects.filter(name__in=names)
        return {obj.name: obj for obj in qs}

    def _load_base_colours(
            self, items: Iterable[BaseColourDTO]
    ) -> Dict[str, BaseColour]:
        instances = [BaseColour(name=i.name) for i in items]
        BaseColour.objects.bulk_create(
            instances, batch_size=self.batch_size, ignore_conflicts=True
        )
        names = [i.name for i in items]
        qs = BaseColour.objects.filter(name__in=names)
        return {obj.name: obj for obj in qs}

    def _load_seasons(self, items: Iterable[SeasonDTO]) -> Dict[str, Season]:
        instances = [Season(name=i.name) for i in items]
        Season.objects.bulk_create(
            instances, batch_size=self.batch_size, ignore_conflicts=True
        )
        names = [i.name for i in items]
        qs = Season.objects.filter(name__in=names)
        return {obj.name: obj for obj in qs}

    def _load_usage_types(
            self, items: Iterable[UsageTypeDTO]
    ) -> Dict[str, UsageType]:
        instances = [UsageType(name=i.name) for i in items]
        UsageType.objects.bulk_create(
            instances, batch_size=self.batch_size, ignore_conflicts=True
        )
        names = [i.name for i in items]
        qs = UsageType.objects.filter(name__in=names)
        return {obj.name: obj for obj in qs}

    @staticmethod
    def _build_images_map(items: Iterable[ImageDTO]) -> Dict[int, str]:
        result: Dict[int, str] = {}
        for img in items:
            result.setdefault(img.product_id, img.image_url)
        return result

    def _load_products(
            self,
            items: Iterable[ProductDTO],
            article_type_map: Dict[str, ArticleType],
            base_colour_map: Dict[str, BaseColour],
            season_map: Dict[str, Season],
            usage_type_map: Dict[str, UsageType],
            images_map: Dict[int, str],
    ) -> None:
        to_create: List[Product] = []
        for dto in tqdm(items, desc="Build Product instances"):
            article_type = article_type_map.get(dto.article_type)
            base_colour = base_colour_map.get(dto.base_colour) if dto.base_colour else None
            season = season_map.get(dto.season) if dto.season else None
            usage_type = usage_type_map.get(dto.usage) if dto.usage else None

            display = dto.product_display_name or ""
            slug = f"{slugify(display) or 'product'}-{dto.product_id}"

            to_create.append(
                Product(
                    product_id=dto.product_id,
                    gender=dto.gender,
                    year=dto.year,
                    product_display_name=dto.product_display_name,
                    description=dto.description,
                    image_url=images_map.get(dto.product_id),
                    slug=slug,
                    article_type=article_type,
                    base_colour=base_colour,
                    season=season,
                    usage_type=usage_type,
                )
            )

        for i in tqdm(range(0, len(to_create), self.batch_size), desc="Bulk insert Products"):
            batch = to_create[i: i + self.batch_size]
            Product.objects.bulk_create(batch, batch_size=self.batch_size, ignore_conflicts=True)


class ProductCleaner:
    def __init__(self) -> None:
        self._data_to_delete: List[Tuple[str, object]] = [
            ("Products", Product.objects.all()),
            ("Article types", ArticleType.objects.all()),
            ("Sub-categories", SubCategory.objects.all()),
            ("Master categories", MasterCategory.objects.all()),
            ("Base colours", BaseColour.objects.all()),
            ("Seasons", Season.objects.all()),
            ("Usage types", UsageType.objects.all()),
        ]


    def clean_catalog(self) -> None:
        with transaction.atomic():
            for label, qs in tqdm(self._data_to_delete, desc="Cleaning catalog"):
                count, _ = qs.delete()
                tqdm.write(f"Deleted {count} rows from {label}")