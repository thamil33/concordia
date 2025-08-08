def add_item_to_list(item, target_list=[]):
    """
    Appends a given item to a list.

    If no list is provided, it is intended to create a new empty list,
    add the item to it, and then return the new list.
    """
    target_list.append(item)
    print(f"Item '{item}' added. List is now: {target_list}")
    return target_list

# --- First Usage ---
# Expected: list_one becomes [10]
print("Calling with the first item:")
list_one = add_item_to_list(10)


# --- Second Usage ---
# Expected: list_two becomes [20], independent of list_one
print("\nCalling with the second item (expecting a new list):")
list_two = add_item_to_list(20)


# --- Verification ---
# Let's check the final values and their object IDs.
print(f"\nFinal value of list_one: {list_one}")
print(f"Final value of list_two: {list_two}")
