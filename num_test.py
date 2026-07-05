import numpy as np

# Create a 2D NumPy array
numbers = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

# Print the array

print("Array:")
print(numbers)

# Display the shape of the array (rows, columns)

print("Shape of array:", numbers.shape)

# Display the data type of elements in the array

print("Data type:", numbers.dtype)

# Perform element-wise addition

updated_array = numbers + 2
print("Array after adding 2:")
print(updated_array)

# Calculate the mean value of all elements

mean_value = np.mean(numbers)
print("Mean value:", mean_value)
