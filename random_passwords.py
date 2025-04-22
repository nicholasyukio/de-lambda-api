import random
import string

def generate():
    # Minimum required characters
    lower = random.choice(string.ascii_lowercase)
    upper = random.choice(string.ascii_uppercase)
    number = random.choice(string.digits)
    special = random.choice('!@#%^&*()-_=+')

    # Other chars, until 8
    other = random.choices(string.ascii_letters + string.digits + '!@#%^&*()-_=+', k=4)

    # Combines everything
    password = [lower, upper, number, special] + other
    random.shuffle(password)

    return ''.join(password)

# Example usage
if __name__ == "__main__":
    print(generate())
