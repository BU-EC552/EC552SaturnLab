# EC552 Class Project - SaturnSearch

Authors: Cullen Paulisick, Josh Singh, Ryan Schneider, Nikhil Gupta

# Motivation:
he identification and implementation of new synthetic parts within a larger synthetic design is tedious and prone to human error. Foundries need access to robust data infrastructure. 
 
Imagine if researchers always had a ‘TL;DR’ option for automatically scraping synthetic biology parts from existing publications...


# Functionality Overview:
1. Query PMC database based on abstract user input
Ex: “Biosensor design for constitutive production”
2. Latent Dirichlet Allocation model develops topic distribution
Able to more appropriately recommend papers according to parts request
3. Mine relevant papers for parts relevant to topic distribution
IBM-Watson Natural Language Understanding Cloud
4. Display parts, metadata and sequence data in GUI
Make the export of parts data and metadata simple



Project Setup:
1. Create a Python Virtual Environment
2. Use pip to download dependencies from the dependencies.txt : i.e python3 -m pip install -r dependencies.txt
3. run the command : python SaturnSearchAlpha.py


Credits:
Loading animation provied by loading.io: www.loading.io

