"""
Exemplu de utilizare a environment-ului PettingZoo pentru Micro Battle

Pentru a rula acest exemplu:
    python src/pettingzoo_example.py
"""

from pettingzoo_env import env

def main():
    # Creează environment-ul
    # Opțiuni pentru game_mode: "Survival", "King of the Hill", "Capture the Flag"
    environment = env(game_mode="Survival", render_mode="human")
    
    # Resetează environment-ul
    observations = environment.reset(seed=42)
    
    # Rulează un episod
    max_steps = 1000
    step_count = 0
    
    print("Starting episode...")
    print(f"Agents: {environment.agents}")
    
    for agent in environment.agent_iter():
        if step_count >= max_steps:
            break
        
        observation, reward, termination, truncation, info = environment.last()
        
        if termination or truncation:
            # Agentul a terminat, trece la următorul
            action = None
        else:
            # Alege o acțiune aleatorie (în locul acestuia, poți folosi un model de RL)
            action = environment.action_space(agent).sample()
        
        environment.step(action)
        step_count += 1
        
        # Rendează la fiecare pas (opțional, poate fi lent)
        if step_count % 10 == 0:
            environment.render()
        
        # Afișează informații despre progres
        if step_count % 100 == 0:
            print(f"Step {step_count}, Agent: {agent}, Reward: {reward}")
    
    print("Episode finished!")
    environment.close()

if __name__ == "__main__":
    main()

