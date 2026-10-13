"""
Script de test pentru a verifica integrarea PettingZoo API

Rulează: python src/test_pettingzoo.py
"""

import sys
import traceback

def test_imports():
    """Test 1: Verifică dacă toate import-urile funcționează"""
    print("=" * 60)
    print("TEST 1: Verificare import-uri")
    print("=" * 60)
    
    try:
        import pettingzoo
        print("✓ pettingzoo importat cu succes")
        print(f"  Versiune: {pettingzoo.__version__ if hasattr(pettingzoo, '__version__') else 'N/A'}")
    except ImportError as e:
        print(f"✗ EROARE: Nu se poate importa pettingzoo: {e}")
        print("  Soluție: pip install pettingzoo")
        return False
    
    try:
        from pettingzoo import AECEnv
        print("✓ AECEnv importat cu succes")
    except ImportError as e:
        print(f"✗ EROARE: Nu se poate importa AECEnv: {e}")
        return False
    
    try:
        from pettingzoo.utils import agent_selector, wrappers
        print("✓ Utilitare PettingZoo importate cu succes")
    except ImportError as e:
        print(f"✗ EROARE: Nu se pot importa utilitare: {e}")
        return False
    
    try:
        from gymnasium.spaces import Box
        print("✓ Gymnasium spaces importate cu succes")
    except ImportError as e:
        print(f"✗ EROARE: Nu se poate importa gymnasium: {e}")
        print("  Soluție: pip install gymnasium")
        return False
    
    try:
        from pettingzoo_env import env, MicroBattleEnv
        print("✓ Environment-ul nostru importat cu succes")
    except ImportError as e:
        print(f"✗ EROARE: Nu se poate importa environment-ul: {e}")
        traceback.print_exc()
        return False
    
    print("\n✓ Toate import-urile funcționează!\n")
    return True

def test_environment_creation():
    """Test 2: Verifică dacă environment-ul poate fi creat"""
    print("=" * 60)
    print("TEST 2: Creare environment")
    print("=" * 60)
    
    try:
        from pettingzoo_env import env
        
        # Test fără rendering (mai rapid)
        environment = env(game_mode="Survival", render_mode=None)
        print("✓ Environment creat cu succes (fără rendering)")
        
        # Verifică metadata
        if hasattr(environment, 'metadata'):
            print(f"✓ Metadata: {environment.metadata.get('name', 'N/A')}")
        
        return environment
    except Exception as e:
        print(f"✗ EROARE la crearea environment-ului: {e}")
        traceback.print_exc()
        return None

def test_environment_methods(env):
    """Test 3: Verifică dacă metodele principale funcționează"""
    print("=" * 60)
    print("TEST 3: Verificare metode environment")
    print("=" * 60)
    
    if env is None:
        print("✗ Environment-ul nu a fost creat, skip test")
        return False
    
    try:
        # Test reset
        observations = env.reset(seed=42)
        print("✓ reset() funcționează")
        # Wrapper-urile PettingZoo pot returna None sau observațiile
        if observations is not None:
            print(f"  Observații pentru {len(observations)} agenți")
        else:
            # Dacă wrapper-urile returnează None, verificăm direct din env
            if hasattr(env, 'observations') and env.observations:
                print(f"  Observații disponibile pentru {len(env.observations)} agenți")
            else:
                print("  Observații vor fi disponibile după primul step")
        
        # Verifică agenții
        if hasattr(env, 'agents'):
            print(f"✓ Agenți disponibili: {len(env.agents)}")
            print(f"  Primul agent: {env.agents[0] if env.agents else 'N/A'}")
        
        # Test observation_space
        if env.agents:
            first_agent = env.agents[0]
            obs_space = env.observation_space(first_agent)
            print(f"✓ observation_space() funcționează")
            print(f"  Shape: {obs_space.shape}")
            print(f"  Type: {type(obs_space)}")
        
        # Test action_space
        if env.agents:
            action_space = env.action_space(first_agent)
            print(f"✓ action_space() funcționează")
            print(f"  Shape: {action_space.shape}")
            print(f"  Type: {type(action_space)}")
            print(f"  Low: {action_space.low}")
            print(f"  High: {action_space.high}")
        
        return True
    except Exception as e:
        print(f"✗ EROARE la testarea metodelor: {e}")
        traceback.print_exc()
        return False

def test_agent_iteration(env):
    """Test 4: Verifică dacă agent_iter funcționează"""
    print("=" * 60)
    print("TEST 4: Verificare agent_iter")
    print("=" * 60)
    
    if env is None:
        print("✗ Environment-ul nu a fost creat, skip test")
        return False
    
    try:
        env.reset(seed=42)
        
        # Test agent_iter
        agent_count = 0
        max_agents_to_test = 5  # Testăm doar primii 5 agenți
        
        for agent in env.agent_iter():
            if agent_count >= max_agents_to_test:
                break
            
            # Verifică last()
            observation, reward, termination, truncation, info = env.last()
            print(f"✓ Agent {agent}: obs_shape={observation.shape}, reward={reward}, terminated={termination}")
            
            # Test step cu acțiune aleatorie
            if not termination and not truncation:
                action = env.action_space(agent).sample()
                env.step(action)
                print(f"  ✓ step() executat cu succes pentru {agent}")
            
            agent_count += 1
        
        print(f"\n✓ agent_iter() funcționează pentru {agent_count} agenți")
        return True
    except Exception as e:
        print(f"✗ EROARE la testarea agent_iter: {e}")
        traceback.print_exc()
        return False

def test_full_episode(env):
    """Test 5: Rulează un episod complet (scurt)"""
    print("=" * 60)
    print("TEST 5: Episod complet (10 pași)")
    print("=" * 60)
    
    if env is None:
        print("✗ Environment-ul nu a fost creat, skip test")
        return False
    
    try:
        env.reset(seed=42)
        step_count = 0
        max_steps = 10
        
        for agent in env.agent_iter():
            if step_count >= max_steps:
                break
            
            observation, reward, termination, truncation, info = env.last()
            
            if termination or truncation:
                action = None
            else:
                action = env.action_space(agent).sample()
            
            env.step(action)
            step_count += 1
        
        print(f"✓ Episod complet executat: {step_count} pași")
        return True
    except Exception as e:
        print(f"✗ EROARE la rularea episodului: {e}")
        traceback.print_exc()
        return False

def main():
    """Rulează toate testele"""
    print("\n" + "=" * 60)
    print("TESTARE INTEGRARE PETTINGZOO API")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Import-uri
    results.append(("Import-uri", test_imports()))
    
    if not results[0][1]:
        print("\n✗ Testele au eșuat la import-uri. Verifică dependențele!")
        return
    
    # Test 2: Creare environment
    env = test_environment_creation()
    results.append(("Creare environment", env is not None))
    
    # Test 3: Metode
    if env:
        results.append(("Metode environment", test_environment_methods(env)))
    
    # Test 4: Agent iteration
    if env:
        results.append(("Agent iteration", test_agent_iteration(env)))
    
    # Test 5: Episod complet
    if env:
        results.append(("Episod complet", test_full_episode(env)))
    
    # Rezumat
    print("\n" + "=" * 60)
    print("REZUMAT TESTE")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nRezultat: {passed}/{total} teste au trecut")
    
    if passed == total:
        print("\nTOATE TESTELE AU TRECUT! PettingZoo API este integrat corect!")
    else:
        print(f"\n! {total - passed} teste au eșuat. Verifică erorile de mai sus.")
    
    # Cleanup
    if env:
        try:
            env.close()
        except:
            pass

if __name__ == "__main__":
    main()

