import kumiho
import time
import uuid
import random
import logging

# Configure logging for the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def unique_name(prefix: str) -> str:
    """Generates a unique name with a prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def test_product_search_performance():
    """
    Generates a large number of products and measures creation and search time.
    """
    root_group_name = unique_name('perf_test')
    num_projects = 5
    num_sequences_per_project = 10
    num_shots_per_sequence = 20
    num_products_per_shot = 5
    total_products = num_projects * num_sequences_per_project * num_shots_per_sequence * num_products_per_shot
    
    product_types = ["model", "dataset", "rig", "texture", "animation"]
    created_product_names = []

    logging.info(f"--- Performance Test Started ---")
    logging.info(f"Root group for this run: {root_group_name}")
    logging.info(f"Will create {total_products} products across a nested hierarchy.")

    # --- 1. Data Creation ---
    start_creation = time.perf_counter()
    
    # Create root group (top-level)
    root_group = kumiho.create_group(root_group_name)
    for i in range(num_projects):
        # Create project group under root
        proj_group = root_group.create_group(f"proj_{i:02d}")
        for j in range(num_sequences_per_project):
            # Create sequence group under project
            seq_group = proj_group.create_group(f"seq_{j:03d}")
            for k in range(num_shots_per_sequence):
                # Create shot group under sequence
                shot_group = seq_group.create_group(f"shot_{k:04d}")
                for l in range(num_products_per_shot):
                    ptype = random.choice(product_types)
                    pname = unique_name(f"asset_{l}")
                    item = kumiho.create_product(shot_group.path, pname, ptype)  # Note: create_product still uses path + name + type
                    logging.info(f"Created product: {item.kref.uri}")
                    if l == 0:  # Store one name per shot for later search test
                        created_product_names.append(pname)

    end_creation = time.perf_counter()
    creation_time = end_creation - start_creation
    logging.info(f"[REPORT] Data Creation Time: {creation_time:.4f} seconds.")
    logging.info(f"[REPORT] Avg time per product: {(creation_time / total_products) * 1000:.4f} ms.")

    # --- 2. Search Performance ---
    logging.info("--- Starting Search Benchmarks ---")

    # A) Search by type (broad)
    start_search_type = time.perf_counter()
    results_type = kumiho.product_search(ptype_filter="model")
    end_search_type = time.perf_counter()
    logging.info(f"[REPORT] Search by Type ('model'): Found {len(results_type)} results in {end_search_type - start_search_type:.4f} seconds.")

    # B) Search by context (medium)
    search_context = f"{root_group_name}/proj_01/seq_001"
    start_search_context = time.perf_counter()
    results_context = kumiho.product_search(context_filter=search_context)
    end_search_context = time.perf_counter()
    logging.info(f"[REPORT] Search by Context ('{search_context}'): Found {len(results_context)} results in {end_search_context - start_search_context:.4f} seconds.")

    # C) Search by name (specific)
    search_name = random.choice(created_product_names)
    start_search_name = time.perf_counter()
    results_name = kumiho.product_search(name_filter=search_name)
    end_search_name = time.perf_counter()
    logging.info(f"[REPORT] Search by Name ('{search_name}'): Found {len(results_name)} results in {end_search_name - start_search_name:.4f} seconds.")

    # --- 3. Teardown ---
    logging.info(f"--- Tearing down test data ---")
    start_delete = time.perf_counter()
    kumiho.delete_group(f"/{root_group_name}", force=True)
    end_delete = time.perf_counter()
    logging.info(f"[REPORT] Teardown Time: {end_delete - start_delete:.4f} seconds.")
    
    logging.info(f"--- Performance Test Finished ---")