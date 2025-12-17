
def get_ontology(department):
    
    if department.lower() == "finance":
        with open(file="ontology/Finance.json", mode="r") as finance:
            return finance
    elif department.lower() == "sales":
        with open(file="ontology/Sales.json", mode="r") as sales:
            return sales
    elif department.lower() == "human resources":
        with open(file="ontology/HumanResources.json") as hr:
            return hr
    else:
        # Return an sse event signifying error in department name
        return
    
 