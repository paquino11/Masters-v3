import matplotlib.pyplot as plt

# Sample data
categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
values = [2.5, 4.0, 3.0, 3.5]

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2)

# Bar plot
ax1.bar(categories, values)
ax1.set_xlabel('Categories')
ax1.set_ylabel('Values')
ax1.set_title('Bar Plot')

# Circle plot
ax2.pie(values, labels=categories)
ax2.set_title('Circle Plot')

# Adjust spacing between subplots
plt.subplots_adjust(wspace=0.5)

# Display the plots
plt.show()
