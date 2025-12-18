from uuid import UUID                                                                                                  
from datetime import datetime                                                                                          
                                                                                                                         
from fastapi import APIRouter, HTTPException                                                                           
from app.db.connection import db                                                                                       
from app.services.embeddings import embedding_service                                                                  
from app.agents.coordinator import run_simulation, get_all_leaders                                                     
from app.models.schemas import (                                                                                       
    SimulationRequest,                                                                                                 
    SimulationResponse,                                                                                                
    LeaderResult,                                                                                                      
    LeaderProfile,                                                                                                     
    SimulationSummary,                                                                                                 
)                                                                                                                      
                                                                                                                         
router = APIRouter(prefix="/api")

@router.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    embedding = await embedding_service.embed(request.text)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
    
    event_row = await db.fetchrow(f"""
                                  INSERT INTO events(text, embedding)
                                  VALUES ($1, '{embedding_str}'::vector)
                                  RETURNING id, created_at
                                  """, request.text)
    
    event_id = event_row["id"]
    sim_row = await db.fetchrow("""
                                INSERT INTO simulations (event_id)
                                VALUES($1)
                                RETURNING id, created_at
                                """, event_id)
    
    simulation_id = sim_row["id"]
    created_at = sim_row["created_at"]
    
    results = await run_simulation(request.text)
    for result in results:                                                                                             
          # Get leader ID                                                                                                
          leader_row = await db.fetchrow(                                                                                
              "SELECT id FROM leader_profiles WHERE name = $1",                                                          
              result["leader"]                                                                                           
          )                                                                                                              
                                                                                                                         
          await db.execute("""                                                                                           
                          INSERT INTO leader_sim_results                                                                             
                          (simulation_id, leader_id, escalation_score, reaction, rationale)                                      
                          VALUES ($1, $2, $3, $4, $5)                                                                                
                          """,                                                                                                           
            simulation_id,                                                                                             
            leader_row["id"],                                                                                          
            result["escalation_score"],                                                                                
            result["reaction"],                                                                                        
            result["rationale"],                                                                                       
          )
    
                                                                                                 
    return SimulationResponse(                                                                                         
        simulation_id=simulation_id,                                                                                   
        event_text=request.text,                                                                                       
        created_at=created_at,                                                                                         
        results=[                                                                                                      
            LeaderResult(                                                                                              
                leader=r["leader"],                                                                                    
                escalation_score=r["escalation_score"],                                                                
                reaction=r["reaction"],                                                                                
                rationale=r["rationale"],                                                                              
                similar_events=r["similar_events"],                                                                    
            )                                                                                                          
            for r in results                                                                                           
        ],                                                                                                             
      )                                                                                                                  
            
    
@router.get("/leaders", response_model=list[LeaderProfile])                                                        
async def list_leaders():                                                                                          
    leaders = await get_all_leaders()                                                                              
    return [LeaderProfile(**leader) for leader in leaders] 


@router.get("/history", response_model=list[SimulationSummary])                                                    
async def get_history():                                                                                           
    rows = await db.fetch("""                                                                                      
          SELECT                                                                                                     
              s.id as simulation_id,                                                                                 
              e.text as event_text,                                                                                  
              s.created_at,                                                                                          
              AVG(r.escalation_score) as avg_escalation                                                              
          FROM simulations s                                                                                         
          JOIN events e ON s.event_id = e.id                                                                         
          JOIN leader_sim_results r ON r.simulation_id = s.id                                                        
          GROUP BY s.id, e.text, s.created_at                                                                        
          ORDER BY s.created_at DESC                                                                                 
          LIMIT 20                                                                                                   
      """)                                                                                                           
                                                                                                                     
    return [                                                                                                       
          SimulationSummary(                                                                                         
              simulation_id=row["simulation_id"],                                                                    
              event_text=row["event_text"],                                                                          
              created_at=row["created_at"],                                                                          
              avg_escalation=round(row["avg_escalation"], 2),                                                        
          )                                                                                                          
          for row in rows                                                                                            
    ] 