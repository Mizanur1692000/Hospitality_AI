"""
Integration Tests for Restaurant Data File Loading

Verifies that the hospitality_ai_agent can successfully connect to and load
data files from the restaurant_inventory_app.

These tests ensure:
1. RESTAURANT_DATA_DIR environment variable is set correctly
2. All required data files exist and are readable
3. Data files contain valid JSON
4. Data can be loaded successfully
"""

import json
import os
import pytest
from pathlib import Path

from backend.consulting_services.menu.analysis_functions import (
    verify_data_files,
    load_restaurant_data
)


class TestDataIntegration:
    """Test suite for restaurant data integration."""

    @pytest.fixture
    def data_dir(self):
        """Get the restaurant data directory from environment."""
        data_dir = os.getenv("RESTAURANT_DATA_DIR")
        if not data_dir:
            pytest.skip("RESTAURANT_DATA_DIR environment variable not set")
        return data_dir

    @pytest.fixture
    def data_paths(self, data_dir):
        """Return paths to all required data files."""
        return {
            "recipes": os.path.join(data_dir, "recipes.json"),
            "menu_items": os.path.join(data_dir, "menu_items.json"),
            "sales_data": os.path.join(data_dir, "sales_data.json")
        }

    def test_environment_variable_set(self):
        """Test that RESTAURANT_DATA_DIR environment variable is configured."""
        data_dir = os.getenv("RESTAURANT_DATA_DIR")
        assert data_dir is not None, (
            "RESTAURANT_DATA_DIR environment variable not set. "
            "Add it to .env file pointing to restaurant_inventory_app/data/"
        )
        assert data_dir != "", "RESTAURANT_DATA_DIR should not be empty"

    def test_data_directory_exists(self, data_dir):
        """Test that the data directory exists."""
        path = Path(data_dir)
        assert path.exists(), f"Data directory does not exist: {data_dir}"
        assert path.is_dir(), f"Data directory path is not a directory: {data_dir}"

    def test_required_files_exist(self, data_paths):
        """Test that all required data files exist."""
        for name, path in data_paths.items():
            file_path = Path(path)
            assert file_path.exists(), f"Missing required file: {name} at {path}"
            assert file_path.is_file(), f"Path is not a file: {name} at {path}"

    def test_files_are_readable(self, data_paths):
        """Test that all data files are readable."""
        for name, path in data_paths.items():
            assert os.access(path, os.R_OK), f"File not readable: {name} at {path}"

    def test_files_not_empty(self, data_paths):
        """Test that data files are not empty."""
        for name, path in data_paths.items():
            file_size = Path(path).stat().st_size
            assert file_size > 0, f"File is empty: {name} at {path}"

    def test_files_contain_valid_json(self, data_paths):
        """Test that all data files contain valid JSON."""
        for name, path in data_paths.items():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                assert data is not None, f"File contains null JSON: {name}"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {name} at {path}: {e}")

    def test_verify_data_files_success(self, data_paths):
        """Test verify_data_files function with valid paths."""
        # Should not raise any exception
        verify_data_files(
            data_paths["recipes"],
            data_paths["menu_items"],
            data_paths["sales_data"]
        )

    def test_verify_data_files_missing_file(self):
        """Test verify_data_files raises error for missing files."""
        with pytest.raises(FileNotFoundError) as exc_info:
            verify_data_files(
                "/nonexistent/recipes.json",
                "/nonexistent/menu_items.json",
                "/nonexistent/sales_data.json"
            )
        assert "Missing required data files" in str(exc_info.value)

    def test_load_restaurant_data_success(self, data_paths):
        """Test that restaurant data loads successfully."""
        recipes, menu_items, sales = load_restaurant_data(
            data_paths["recipes"],
            data_paths["menu_items"],
            data_paths["sales_data"]
        )

        # Verify data structures
        assert isinstance(recipes, dict), "Recipes should be a dictionary"
        assert isinstance(menu_items, dict), "Menu items should be a dictionary"
        assert isinstance(sales, dict), "Sales data should be a dictionary"

        # Verify data is not empty
        assert len(recipes) > 0, "Recipes data is empty"
        assert len(menu_items) > 0, "Menu items data is empty"
        assert len(sales) > 0, "Sales data is empty"

    def test_loaded_data_structure(self, data_paths):
        """Test that loaded data has expected structure."""
        recipes, menu_items, sales = load_restaurant_data(
            data_paths["recipes"],
            data_paths["menu_items"],
            data_paths["sales_data"]
        )

        # Check recipes structure (keyed by recipe_id)
        for recipe_id, recipe in recipes.items():
            assert isinstance(recipe_id, str), "Recipe ID should be a string"
            assert "recipe_name" in recipe, f"Recipe {recipe_id} missing 'recipe_name'"
            assert "total_cost" in recipe, f"Recipe {recipe_id} missing 'total_cost'"

        # Check menu items structure (keyed by menu_item_id)
        for item_id, item in menu_items.items():
            assert isinstance(item_id, str), "Menu item ID should be a string"
            assert "menu_name" in item, f"Menu item {item_id} missing 'menu_name'"
            assert "price" in item, f"Menu item {item_id} missing 'price'"

        # Check sales structure (keyed by menu_item_id)
        for item_id, sales_data in sales.items():
            assert isinstance(item_id, str), "Sales item ID should be a string"
            assert "total_units_sold" in sales_data, f"Sales {item_id} missing 'total_units_sold'"
            assert "total_revenue" in sales_data, f"Sales {item_id} missing 'total_revenue'"

    def test_data_integration_end_to_end(self, data_paths):
        """
        End-to-end test: Verify data can be loaded and joined for analysis.

        This test simulates what the menu engineering tasks do:
        1. Load all data files
        2. Verify data integrity
        3. Confirm data is ready for analysis
        """
        # Load data
        recipes, menu_items, sales = load_restaurant_data(
            data_paths["recipes"],
            data_paths["menu_items"],
            data_paths["sales_data"]
        )

        # Verify we can match menu items to recipes
        matched_items = 0
        for item_id, item in menu_items.items():
            recipe_id = item.get("recipe_id")
            if recipe_id and recipe_id in recipes:
                matched_items += 1

        assert matched_items > 0, "No menu items matched to recipes"

        # Verify we have sales data for menu items
        items_with_sales = 0
        for item_id in menu_items.keys():
            if item_id in sales:
                items_with_sales += 1

        assert items_with_sales > 0, "No menu items have sales data"

        # Success: Data is properly integrated and ready for analysis
        print(f"\n✅ Data Integration Test Passed:")
        print(f"   - Loaded {len(recipes)} recipes")
        print(f"   - Loaded {len(menu_items)} menu items")
        print(f"   - Loaded sales data for {len(sales)} items")
        print(f"   - Matched {matched_items} items to recipes")
        print(f"   - Found sales data for {items_with_sales} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
