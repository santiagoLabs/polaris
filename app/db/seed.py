import asyncio
from app.db.connection import db
from app.services.embeddings import embedding_service

LEADER_PROFILES = [                                                                                               
      {                                                                                                             
          "name": "Revisionist Expansionist",                                                                       
          "aggression": 8,                                                                                          
          "diplomacy": 3,                                                                                           
          "risk_tolerance": 8,                                                                                      
          "domestic_pressure": 6,                                                                                   
          "escalation_threshold": 4,  # Low threshold = escalates easily                                            
      },                                                                                                            
      {                                                                                                             
          "name": "Status-quo Diplomat",                                                                            
          "aggression": 2,                                                                                          
          "diplomacy": 9,                                                                                           
          "risk_tolerance": 3,                                                                                      
          "domestic_pressure": 4,                                                                                   
          "escalation_threshold": 8,  # High threshold = resists escalation                                         
      },                                                                                                            
      {                                                                                                             
          "name": "Crisis Populist",                                                                                
          "aggression": 6,                                                                                          
          "diplomacy": 4,                                                                                           
          "risk_tolerance": 7,                                                                                      
          "domestic_pressure": 9,  # Heavily influenced by domestic opinion                                         
          "escalation_threshold": 5,                                                                                
      },                                                                                                            
      {                                                                                                             
          "name": "Isolationist Stabilizer",                                                                        
          "aggression": 2,                                                                                          
          "diplomacy": 5,                                                                                           
          "risk_tolerance": 2,                                                                                      
          "domestic_pressure": 7,                                                                                   
          "escalation_threshold": 9,  # Very high = avoids conflict                                                 
      },                                                                                                            
]

HISTORICAL_EVENTS = [                                                                                                
      "Naval blockade imposed on island nation, restricting essential supplies and military equipment",                
      "Military forces mass at disputed border region following ethnic tensions",                                      
      "Cyber attack disables critical infrastructure in capital city",                                                 
      "Disputed election results spark mass protests and international concern",                                       
      "Aircraft shot down over contested airspace, casualties reported",                                               
      "Trade embargo imposed following human rights violations",                                                       
      "Military coup overthrows democratically elected government",                                                    
      "Nuclear facility detected in violation of international agreements",                                            
      "Border skirmish escalates with artillery exchanges",                                                            
      "Assassination of political leader triggers regional instability",                                               
      "Refugee crisis overwhelms neighboring countries",                                                               
      "Naval vessels collide in disputed waters",                                                                      
      "Economic sanctions target ruling elite and state institutions",                                                 
      "Peacekeeping forces attacked by unknown militants",                                                             
      "Territory annexed following disputed referendum",                                                               
] 

async def seed_leaders():                                                                                                                                                                                                                                                                                                                                                                                                     
        for leader in LEADER_PROFILES:                                                                            
            # Check if leader already exists                                                                      
            existing = await db.fetchrow(                                                                         
                "SELECT id FROM leader_profiles WHERE name = $1",                                                 
                leader["name"]                                                                                    
            )                                                                                                     
                                                                                                                    
            if existing:                                                                                          
                print(f"Leader '{leader['name']}' already exists, skipping")                                      
                continue                                                                                          
                                                                                                                    
            # Insert new leader                                                                                   
            await db.execute(                                                                                     
                """                                                                                               
                INSERT INTO leader_profiles                                                                       
                (name, aggression, diplomacy, risk_tolerance, domestic_pressure, escalation_threshold)        
                VALUES ($1, $2, $3, $4, $5, $6)                                                                   
                """,                                                                                              
                leader["name"],                                                                                   
                leader["aggression"],                                                                             
                leader["diplomacy"],                                                                              
                leader["risk_tolerance"],                                                                         
                leader["domestic_pressure"],                                                                      
                leader["escalation_threshold"],                                                                   
            )                                                                                                     
            print(f"Inserted leader: {leader['name']}")                                                                                                                                           

async def seed_events():                                                                                             
    """Insert historical events with embeddings."""                                                                  
    # Check how many events exist                                                                                    
    result = await db.fetchrow("SELECT COUNT(*) as count FROM events")                                               
    if result["count"] >= len(HISTORICAL_EVENTS):                                                                    
        print(f"Events already seeded ({result['count']} exist), skipping")                                          
        return                                                                                                       
                                                                                                                       
    print(f"Generating embeddings for {len(HISTORICAL_EVENTS)} events...")                                           
                                                                                                                       
    # Batch embed all events at once (faster)                                                                        
    embeddings = await embedding_service.embed_batch(HISTORICAL_EVENTS)                                              
                                                                                                                       
    for text, embedding in zip(HISTORICAL_EVENTS, embeddings):                                                       
        # Convert embedding list to pgvector format                                                                  
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"                                              
        await db.execute(                                                                                            
            """                                                                                                      
            INSERT INTO events (text, embedding)                                                                     
            VALUES ($1, $2::vector)                                                                                  
            """,                                                                                                     
            text,                                                                                                    
            embedding_str,                                                                                           
        )                                                                                                            
        
        print(f"Inserted event: {text[:50]}...")                                                                     
                                                                                                                       
    print(f"Seeded {len(HISTORICAL_EVENTS)} historical events")     

async def seed_all():                                                                                 
    """Run all seed functions."""                                                                     
    await db.connect()                                                                                
                                                                                                        
    try:                                                                                              
        await seed_leaders()                                                                          
        await seed_events()                                                                           
    finally:                                                                                          
        await db.disconnect()                                                                                                     
                                                                                                                    
if __name__ == "__main__":                                                                                        
    asyncio.run(seed_all()) 