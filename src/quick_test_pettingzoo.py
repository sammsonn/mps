"""
Test rapid pentru a verifica dacă PettingZoo environment funcționează
"""

from pettingzoo_env import env

print("Test rapid PettingZoo...")

# Creează environment
try:
    env_instance = env(game_mode="Survival", render_mode=None)
    print("✓ Environment creat")
except Exception as e:
    print(f"✗ Eroare la creare: {e}")
    exit(1)

# Test reset
try:
    obs = env_instance.reset(seed=42)
    print(f"✓ reset() funcționează")
    if obs is not None:
        print(f"  Observații: {len(obs)} agenți")
    else:
        print("  (Wrapper-urile returnează None, dar e OK)")
except Exception as e:
    print(f"✗ Eroare la reset: {e}")
    exit(1)

# Test observe
try:
    if env_instance.agents:
        first_agent = env_instance.agents[0]
        observation = env_instance.observe(first_agent)
        print(f"✓ observe() funcționează pentru {first_agent}")
        print(f"  Observation shape: {observation.shape}")
    else:
        print("⚠ Nu există agenți disponibili")
except Exception as e:
    print(f"✗ Eroare la observe: {e}")
    traceback.print_exc()
    exit(1)

# Test action_space și observation_space
try:
    if env_instance.agents:
        first_agent = env_instance.agents[0]
        obs_space = env_instance.observation_space(first_agent)
        act_space = env_instance.action_space(first_agent)
        print(f"✓ observation_space() funcționează: {obs_space.shape}")
        print(f"✓ action_space() funcționează: {act_space.shape}")
except Exception as e:
    print(f"✗ Eroare la spaces: {e}")
    exit(1)

# Test un pas simplu
try:
    if env_instance.agents:
        first_agent = env_instance.agents[0]
        action = env_instance.action_space(first_agent).sample()
        env_instance.step(action)
        print(f"✓ step() funcționează")
except Exception as e:
    print(f"✗ Eroare la step: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n🎉 Toate testele de bază au trecut!")
print("Environment-ul PettingZoo este integrat corect!")

env_instance.close()

