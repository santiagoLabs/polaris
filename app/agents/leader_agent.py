import json
from anthropic import AsyncAnthropic
from app.config import settings
from app.services.vector_search import find_similar_events

client = AsyncAnthropic(api_key = settings.anthropic_api_key)
SYSTEM_PROMPT = """You are simulating a world leader archetype analyzing a geopolitical crisis.                   
  ## Your Leader Profile: {leader_name}                                                                             
                                                                                                                    
  Behavioral traits (scale 0-10):                                                                                   
  - Aggression: {aggression}/10                                                                                     
  - Diplomacy: {diplomacy}/10                                                                                       
  - Risk Tolerance: {risk_tolerance}/10                                                                             
  - Domestic Pressure Sensitivity: {domestic_pressure}/10                                                           
  - Escalation Threshold: {escalation_threshold}/10                                                                 
                                                                                                                    
  ## Your Task                                                                                                      
                                                                                                                    
  Analyze the crisis event and predict how this leader archetype would respond.                                     
  Consider your traits carefully - they should influence your reasoning and decision.                               
                                                                                                                    
  ## Similar Historical Events (for context)                                                                        
  {similar_events}                                                                                                  
                                                                                                                    
  ## Response Format                                                                                                
                                                                                                                    
  You MUST respond with valid JSON only, no other text:                                                             
  {{                                                                                                                
      "escalation_score": <float 0-10, where 10 is maximum escalation>,                                             
      "reaction": "<short action description, 2-5 words>",                                                          
      "rationale": "<1-2 sentence explanation of why this leader would react this way>"                             
  }}                                                                                                                
  """

async def run_leader_agent(leader: dict, event_text: str, similar_events: list[dict]) -> dict:
    events_context = "\n".join(
        f"- {e['text']} (similarity: {e['similarity']})"
        for e in similar_events
    ) or "No similar events found."
    
    system = SYSTEM_PROMPT.format(                                                                                
        leader_name=leader["name"],                                                                               
        aggression=leader["aggression"],                                                                          
        diplomacy=leader["diplomacy"],                                                                            
        risk_tolerance=leader["risk_tolerance"],                                                                  
        domestic_pressure=leader["domestic_pressure"],                                                            
        escalation_threshold=leader["escalation_threshold"],                                                      
        similar_events=events_context,                                                                            
    )
    
    response = await client.messages.create(
        model = "claude-sonnet-4-20250514",
        max_tokens = 500,
        system = system,
        messages=[
            {"role": "user", "content": f"Crisis Event: {event_text}"}
        ],
    )
    
    response_text = response.content[0].text 
    
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "escalation_score": 5.0,
            "reaction": "Response unclear",
            "rationale": response_text[:200],
        }
        
    return {
        "leader": leader["name"],                                                                                 
        "escalation_score": float(result.get("escalation_score", 5.0)),                                           
        "reaction": result.get("reaction", "Unknown"),                                                            
        "rationale": result.get("rationale", "No rationale provided"),                                            
        "similar_events": [e["text"] for e in similar_events], 
    } 