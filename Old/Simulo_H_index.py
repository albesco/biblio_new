# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 12:55:13 2024

@author: Paolo Castellini
"""

import matplotlib.pyplot as plt


pub_year=2
cit_year_paper=2



docs=[]
cits=[]
d=0
c=0
years=[]
for year in range(1980,2025):
    print(year)
    d=d+pub_year
    c=c+cit_year_paper*d
    docs.append(d)
    cits.append(c)
    years.append(year)




plt.figure(figsize=(8, 5))
plt.plot(years, docs, marker='o', linestyle='-', color='b', label='H-inder in Years')

# Add labels, title, and legend
plt.xlabel('Years')
plt.ylabel('Docs')
plt.title('Average Authors per Year')
plt.grid(True)
plt.legend()

# Show the plot
plt.show()



plt.figure(figsize=(8, 5))
plt.plot(years, cits, marker='o', linestyle='-', color='b', label='H-inder in Years')

# Add labels, title, and legend
plt.xlabel('Years')
plt.ylabel('Cits')
plt.title('Average Authors per Year')
plt.grid(True)
plt.legend()

# Show the plot
plt.show()


