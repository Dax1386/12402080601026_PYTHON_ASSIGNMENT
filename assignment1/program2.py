import re

class AhoCorasick:
    def __init__(self):
        self.trie = [{}]
        self.output = [[]]
        self.fail = [0]

    def add_word(self, word):
        node = 0
        for char in word:
            if char not in self.trie[node]:
                self.trie[node][char] = len(self.trie)
                self.trie.append({})
                self.output.append([])
                self.fail.append(0)
            node = self.trie[node][char]
        self.output[node].append(word)

    def build(self):
        queue = []
        for char, next_node in self.trie[0].items():
            queue.append(next_node)
        while queue:
            curr = queue.pop(0)
            for char, next_node in self.trie[curr].items():
                queue.append(next_node)
                f = self.fail[curr]
                while f > 0 and char not in self.trie[f]:
                    f = self.fail[f]
                self.fail[next_node] = self.trie[f][char] if char in self.trie[f] else 0
                self.output[next_node].extend(self.output[self.fail[next_node]])

    def contains_any(self, text):
        node = 0
        text = text.lower()
        for char in text:
            while node > 0 and char not in self.trie[node]:
                node = self.fail[node]
            node = self.trie[node].get(char, 0)
            if self.output[node]:
                return True
        return False

def audit_passwords(banned_words, passwords):
    ac = AhoCorasick()
    for word in banned_words:
        if word:
            ac.add_word(word.lower())
    ac.build()
    
    special_chars = set("!@#$%^&*()_+-=[]{}|;:'\",.<>/?")
    
    for idx, pwd in enumerate(passwords, 1):
        if len(pwd) < 6 or len(pwd) > 12:
            print(f"{idx}: WEAK_LENGTH")
            continue
            
        if ac.contains_any(pwd):
            print(f"{idx}: COMPROMISED")
            continue
            
        # Check consecutive repeat > 3
        repeat_found = False
        count = 1
        for i in range(1, len(pwd)):
            if pwd[i] == pwd[i-1]:
                count += 1
                if count > 3:
                    repeat_found = True
                    break
            else:
                count = 1
                
        has_lower = any(c.islower() for c in pwd)
        has_upper = any(c.isupper() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        has_special = any(c in special_chars for c in pwd)
        
        if repeat_found or not (has_lower and has_upper and has_digit and has_special):
            print(f"{idx}: WEAK_PATTERN")
        else:
            print(f"{idx}: STRONG")

# Sample Execution
if __name__ == "__main__":
    banned = ["admin", "college"]
    pwds = ["Abc12@", "adminA1@", "AAAA1@b", "short", "Good9#"]
    audit_passwords(banned, pwds)