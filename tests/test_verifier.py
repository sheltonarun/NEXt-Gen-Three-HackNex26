from agent.executor import save_script
from verifier.verify import verify

path = save_script("print(1234.5)", "demo")
print(verify(path, 1234.5, ground_truth=1234.5))   # passed True
print(verify(path, 999))                           # passed False