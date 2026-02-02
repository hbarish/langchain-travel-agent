from dotenv import load_dotenv
load_dotenv()

from agent import create_travel_agent

agent = create_travel_agent()

trip_input = """
City1: New York City, USA 2026-01-31
Central Park;8am-9am
The Metropolitan Museum of Art;10am-12pm
Statue of Liberty;12pm-13pm
American Museum of Natural History;13pm-15pm
Grand Central Terminal;16pm-18pm

City2: Honolulu Hawai'i 2026-02-01
Hawaiʻi Volcanoes National Park;9am-11am

City3: Los Angeles, CA 2026-02-02
Griffith Park;8am-9am
Griffith Observatory;10am-11am
Old Los Angeles Zoo;12pm-13pm

City4: Vancouver, BC, Canada 2026-02-03
VanDusen Botanical Garden;10am-12pm
Vancouver Aquarium;12pm-14pm
Science World;14pm-17pm
""".strip()

response = agent.invoke(
    {"messages": [("user", trip_input)]},
    config={"configurable": {"thread_id": "michael-trip"}}
)

print(response["messages"][-1].content)