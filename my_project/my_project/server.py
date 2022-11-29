import mesa

from my_project.agents import Person, Influencer, Territory, PoliticalParty
from my_project.model import Simulation

# To be able to use custom images as "Shape" grid should be CanvasGrid not Hex
## portrayal["Shape"] = "my_project/resources/republican.png"
## portrayal["Shape"] = "my_project/resources/democrat.png"
## portrayal["Shape"] = "my_project/resources/person.png"

def person_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Person:
        if agent.political_party == PoliticalParty.RED:
            portrayal["Shape"] = "my_project/resources/republican.png"
            # portrayal["Color"] = ["#80120E"]
        elif agent.political_party == PoliticalParty.BLUE:
            portrayal["Shape"] = "my_project/resources/democrat.png"
            # portrayal["Color"] = ["#112380"]
        else:
            portrayal["Shape"] = "my_project/resources/person.png"
            # portrayal["Color"] = ["#9E9E9E"]
        # portrayal["r"] = 0.3
        portrayal["scale"] = 0.8
        portrayal["Layer"] = 2

    elif type(agent) is Influencer:
        if agent.political_party == PoliticalParty.RED:
            portrayal["Shape"] = "my_project/resources/republican.png"
            # portrayal["Color"] = ["#80120E"]
        elif agent.political_party == PoliticalParty.BLUE:
            portrayal["Shape"] = "my_project/resources/democrat.png"
            # portrayal["Color"] = ["#112380"]
        else:
            portrayal["Shape"] = "my_project/resources/person.png"
            # portrayal["Color"] = ["#9E9E9E"]
        # portrayal["r"] = 0.6
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    elif type(agent) is Territory:
        color_territory = "#" + str((agent.territory_id+1) * 2) * 6
        if agent.political_party == PoliticalParty.RED:
            portrayal["Color"] = [color_territory,color_territory,color_territory,"#AA0000"]
            # portrayal["Color"] = ["#EE4C4E", "#A83638"]
        elif agent.political_party == PoliticalParty.BLUE:
            portrayal["Color"] = [color_territory,color_territory,color_territory, "#3369E8"]
            # portrayal["Color"] = ["#3369E8", "#264EAB"]
        else:
            portrayal["Color"] = [color_territory]
            # portrayal["Color"] = ["#9E9E9E","#00" + str((agent.territory_id+1) * 2) * 2 + "00"]

        # portrayal["Color"] = ["#" + "FF" if agent.political_party == PoliticalParty.RED else "00" + str(agent.territory_id * 2) * 2 + "FF" if agent.political_party == PoliticalParty.BLUE else "00"]
        # portrayal["Color"] = ["#00" + str((agent.territory_id+1) * 2) * 2 + "00"]

        portrayal["Shape"] = "rect"
        # portrayal["Shape"] = "hex"
        portrayal["Filled"] = "true"
        portrayal["r"] = 1
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Layer"] = 0

    return portrayal

canvas_element = mesa.visualization.CanvasGrid(person_portrayal, 20, 20, 500, 500)
# canvas_element = mesa.visualization.CanvasHexGrid(person_portrayal, 20, 20, 500, 500)
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Person", "Color": "#000000"},
        {"Label": "Influencer", "Color": "#888888"},
        {"Label": "Republican", "Color": "#AA0000"},
        {"Label": "Democrat", "Color": "#0000AA"},
        {"Label": "None", "Color": "#9A9A9A"},
    ]
)
pie_element = mesa.visualization.PieChartModule(
    [
        {"Label": "Republican", "Color": "#AA0000"},
        {"Label": "Democrat", "Color": "#0000AA"},
        {"Label": "None", "Color": "#9A9A9A"},
    ],
    300,300
)

# UI parameters TODO
model_params = {
    # The following line is an example to showcase StaticText.
    "title": mesa.visualization.StaticText("Parameters:"),
    "is_hex": mesa.visualization.Checkbox("Hex Grid Enabled", False),
    "is_mortal": mesa.visualization.Checkbox("Enable Mortality", True),
    "max_age": mesa.visualization.Slider(
        "Maximum Age", 80, 10, 100
    ),
    "enable_territory": mesa.visualization.Checkbox("Territory Enabled", True),
    "number_territory": mesa.visualization.Slider("Number of Territories", 4, 1, 10),
    "title_political": mesa.visualization.StaticText("Political Parameters:"),
    "initial_percentage": mesa.visualization.Slider(
        "Initial Political Difference",
        0.5, 0, 1, 0.01,
        description="The Percentage of Republican/Right or Democrat/Left",
    ),
    "proximity_influence": mesa.visualization.Slider(
        "Proximity Influence", 0.3, 0.1, 1.0, 0.01
    ),
    "title_person": mesa.visualization.StaticText("Person Parameters:"),
    "initial_person": mesa.visualization.Slider(
        "Initial Person Population", 100, 10, 300
    ),
    "person_reproduce": mesa.visualization.Slider(
        "Reproduction Rate", 0.04, 0.01, 1.0, 0.01
    ),
    "title_influencer": mesa.visualization.StaticText("Influencer Parameters:"),
    "enable_influencer": mesa.visualization.Checkbox("Influencer Enabled", True),
    "initial_influencer": mesa.visualization.Slider("Initial Influencer Population", 50, 10, 300),
    "influencer_influence": mesa.visualization.Slider("Influencer Influence", 0.3, 0.1, 1, 0.01),
    "influencer_changes": mesa.visualization.Checkbox(
        "Influencer Consumes Ideas", True,
        description="Determines if Influencers will stay with their ideas or change.",),
    "influencer_reproduce": mesa.visualization.Slider(
        "Influencer Reproduction Rate",
        0.07, 0.01, 1.0, 0.01,
        description="The rate at which influencer agents reproduce.",
    ),
}

server = mesa.visualization.ModularServer(
    Simulation, [canvas_element, pie_element, chart_element], "Political Evolution Model", model_params
)
server.port = 8521
