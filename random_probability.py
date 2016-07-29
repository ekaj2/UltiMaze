import random

def rand_prob(items, probs):
    factor = sum(probs)
    rand = random.random()
    val = round(rand * factor)
    
    i = 0
    while i < len(probs):
        if sum(probs[:i]) <= val <= sum(probs[:i+1]): 
            return items[i]
        i += 1
    

def main():
    items = ["a", "b", "c"]
    probs = [1, 3, 10]
    
    results = []
    for i in range(0, 1000):
        results += [rand_prob(items, probs)]
    a = 0
    b = 0
    c = 0
    for i in results:
        if i == "a":
            a += 1
        elif i == "b":
            b += 1
        elif i == "c":
            c += 1
    print(a,b,c)
        
if __name__ == "__main__":
    main()