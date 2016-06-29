import discord, asyncio, json, os, traceback, math, requests, operator


class Modules:
    pass


class Log:
    def __init__(self):
        self.messages = []
        self.result = None
        self.decorate = True
        self.ctx = None
        self.args = []

    def log(self, msg):
        self.messages.append(msg)

    def clear(self):
        self.messages = []
        self.result = None

    def get(self):
        return self.messages

    def count(self):
        return len(self.messages)


client = discord.Client()
_log = Log()
_m = Modules()

data = {
    "tags": {},
    "code": {},
    "startup": {},
    "open": ":{",
    "close": "}:"
}

def result(v, decorate=False):
    _log.decorate = decorate
    _log.result = v


def log(msg):
    _log.log(msg)


def getargs():
    return _log.args


def getclient():
    return client


def getdata():
    return data


def getctx():
    return _log.ctx


def get_d(n):
    sum = 1
    i = 2
    while i * i < n:
        if n % i == 0:
            sum += i
            sum += int(n/i)
        i += 1
    return sum


def get_sum(n):
    sum = 0
    found = [-1] * n
    for i in range(n):
        d = get_d(i)
        if d < n and found[d] == i and d != i:
            sum += i + d
        found[i] = d
    return sum


def get_seqs(strn, is_number=False):
    strn = strn.lower()
    if is_number:
        digits = "0123456789"
    else:
        digits = "abcdefghijklmnopqrstuvwxyz"

    rising_sequence = strn[0]
    best_rising_sequence = ""
    falling_sequence = strn[0]
    best_falling_sequence = ""
    repeat_sequence = strn[0]
    best_repeat_sequence = ""
    digit_sum = 0
    if is_number:
        digit_sum = int(strn[0])
    for i in range(1, len(strn)):
        if is_number:
            digit_sum += int(strn[i])
        if strn[i] == repeat_sequence[-1]:
            repeat_sequence += strn[i]
        else:
            if len(repeat_sequence) > len(best_repeat_sequence):
                best_repeat_sequence = repeat_sequence
            repeat_sequence = strn[i]

        if digits.find(strn[i]) == digits.find(rising_sequence[-1]) + 1:
            rising_sequence += strn[i]
        else:
            if len(rising_sequence) > len(best_rising_sequence):
                best_rising_sequence = rising_sequence
            rising_sequence = strn[i]

        if digits.find(strn[i]) == digits.find(falling_sequence[-1]) - 1:
            falling_sequence += strn[i]
        else:
            if len(falling_sequence) > len(best_falling_sequence):
                best_falling_sequence = falling_sequence
            falling_sequence = strn[i]

    best_pal = ""
    for digit in digits:
        index = strn.find(digit)
        while index > -1:
            nindex = strn.find(digit, index + 1)
            if nindex != -1:
                substr = strn[index:nindex + 1]
                if len(substr) > len(best_pal):
                    if substr == substr[::-1]:
                        best_pal = "Best palindrome: " + substr
            index = nindex
    if best_pal == "":
        best_pal = "Doesn't contain a palindrome"

    return [rising_sequence, falling_sequence, repeat_sequence, best_pal, digit_sum]


nums = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
tens = ["", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
powers = ["thousand", "million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion", "octillion", "nonillion", "decillion", "undecillion", "duodecillion",
          "tredecillion", "quatttuor-decillion", "quindecillion", "sexdecillion", "septen-decillion", "octodecillion", "novemdecillion", "vigintillion", "centillion"]


def get_word(n):
    if n == 0:
        return "zero"

    is_negative = False
    if n < 0:
        is_negative = True
        n = abs(n)

    strn = str(n)

    word = ""
    power = 0
    had_hundred = False
    while power < len(strn):
        digit = int(strn[-(power+1)])
        if power == 0: # number
            word += nums[digit]
            power += 1
        elif power == 1: #
            if digit == 1:
                word = teens[int(strn[-1])]
            else:
                if word != "":
                    if tens[digit] != "":
                        word = tens[digit] + "-" + word
                else:
                    word = tens[digit]
            power += 1
        elif power == 2:
            if digit > 0:
                if word != "":
                    word = nums[digit] + "-hundred-and-" + word
                else:
                    word = nums[digit] + "-hundred"
                had_hundred = True
            power += 1
        else:
            next_power = min(len(strn), power + 3)
            prefix = get_word(int(strn[-next_power:-power]))

            if prefix != "" and prefix != "zero":
                power_index = math.floor(power/3) - 1
                if word != "":
                    if had_hundred or power_index > 0:
                        word = prefix + "-" + powers[power_index] + "-" + word
                    else:
                        word = prefix + "-" + powers[power_index] + "-and-" + word
                else:
                    word = prefix + "-" + powers[power_index]
            power += 3

    if is_negative:
        return "minus-" + word
    else:
        return word

def find_largest_prime(n):
    factors = []
    if n % 2 == 0:
        factors.append(2)
        while n % 2 == 0:
            n /= 2
        if n == 1:
            return 2

    i = 3
    while i * i < n:
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n /= i
        i += 2
    if n != 1:
        factors.append(int(n))
    return factors

def save():
    f = open("selfbot.dat", "w")
    json.dump(data, f)
    if not f.closed:
        f.close()


def merge(original, override):
    for (key, value) in override.items():
        if key in original:
            if type(value) is list:
                original[key] += value
            elif type(value) is dict:
                merge(original[key], value)
            else:
                original[key] = value
        else:
            original[key] = value


@asyncio.coroutine
def run_eval(code, args=[], ctx=None):
    _log.clear()
    _log.args = args
    _log.ctx = ctx
    try:
        rcode = []
        do_yield = False
        for line in code:
            if line.startswith("import "):
                modname = line[7:]
                print("importing " + modname)
                setattr(_m, modname, __import__(modname))
            else:
                if "yield " in line:
                    do_yield = True
                rcode.append(line)
        if len(rcode) > 0:
            exec("def _temp_f():\n    " + "\n    ".join(rcode), globals())
            if do_yield:
                yield from _temp_f()
            else:
                _temp_f()

        _result = _log.result

        ret = ""
        if _log.count() > 0:
            ret = "```\n" + "\n".join(_log.get()) + "\n```\n"

        if _result is not None:
            if _log.decorate:
                if type(_result) is list:
                    ret += "```\n" + "\n".join(_result) + "\n```"
                elif type(_result) is dict:
                    ret += "```\n" + "\n".join(["%s: %s" % (key, value) for (key, value) in result.items()]) + "\n```"
                else:
                    ret += "`" + str(_result) + "`"
            else:
                ret += str(_result)
        elif ret == "":
            ret = "`Code executed.`"

        return ret
    except Exception:
        return "```\n" + "\n".join(code) + "\n```\n````" "```\n" + traceback.format_exc(20) + "\n```"


def run_command(cmd, ctx=None):
    escaped = False
    if cmd.startswith("\\"):
        cmd = cmd[1:]
        escaped = True
    if cmd.startswith("!") and not escaped:
        spl = cmd[1:].split(" ")
        if spl[0] == "tag":
            data["tags"][spl[1]] = " ".join(spl[2:])
            save()
            return "`Created tag: " + spl[1] + "`"
        elif spl[0] == "eval":
            code = [x for x in [y.replace("```", "").replace("`\\``", "```") for y in " ".join(spl[1:]).split("\n")] if x != "" and x != "py"]
            ret = yield from run_eval(code, ctx=ctx)
            save()
            return ret
        elif spl[0] == "get":
            if spl[1] == "cmd":
                if spl[2] in data["code"]:
                    return "`Code for " + spl[2] + ": `\n\n```\n" + "\n".join(data["code"][spl[2]]) + "\n```"
                else:
                    return "`No code found for " + spl[2] + "`"
            elif spl[1] == "tag":
                if spl[2] in data["tag"]:
                    return "`Tag for " + spl[2] + ": `\n" + data["tags"][spl[2]]
                else:
                    return "`No tag found named " + spl[2] + "`"
            elif spl[1] == "startup":
                if spl[2] in data["startup"]:
                    return "`Code for " + spl[2] + ": `\n\n```\n" + "\n".join(data["startup"][spl[2]]) + "\n```"
                else:
                    return "`No code found for " + spl[2] + "`"
        elif spl[0] == "cmd":
            name = spl[1]
            code = [x for x in [y.replace("`\\``", "¬¬¬").replace("```", "").replace("¬¬¬", "```") for y in " ".join(spl[2:]).split("\n")] if x != "" and x != "py"]
            data["code"][name] = code
            save()
            return "`Created command: " + name + "`"
        elif spl[0] == "open":
            data["open"] = " ".join(spl[1:])
            save()
            return "`Set selfbot command open to " + data["open"] + "`"
        elif spl[0] == "close":
            data["close"] = " ".join(spl[1:])
            save()
            return "`Set selfbot command close to " + data["close"] + "`"
        elif spl[0] == "del":
            if spl[1] == "cmd":
                name = spl[2]
                if name in data["code"]:
                    del data["code"][name]
                    save()
                    return "`Command '" + name + "' deleted`"
                else:
                    return "`No command named '" + name + "'`"
            elif spl[1] == "tag":
                name = spl[2]
                if name in data["tags"]:
                    del data["tags"][name]
                    save()
                    return "`Tag '" + name + "' deleted`"
                else:
                    return "`No tag named '" + name + "'`"
            elif spl[1] == "startup":
                name = spl[2]
                if name in data["startup"]:
                    del data["startup"][name]
                    save()
                    return "`Startup code '" + name + "' deleted`"
                else:
                    return "`No startup code named '" + name + "'`"
            else:
                return "`Invalid delete type, must be cmd, tag or startup`"
        elif spl[0] == "dl":
            url = " ".join(spl[3:])
            text = requests.get(url).text
            if spl[1] == "tag":
                data["tags"][spl[2]] = text
                return "`Downloaded tag " + spl[2] + "`"
            elif spl[1] == "cmd":
                data["code"][spl[2]] = text.split("\n")
                return "`Downloaded command code " + spl[2] + "`"
            elif spl[1] == "startup":
                data["code"][spl[2]] = text.split("\n")
                return "`Downloaded startup code " + spl[2] + "`"
            else:
                return "`Invalid upload type, must be cmd, tag or startup"
        elif spl[0] == "list":
            if spl[1] == "cmd":
                return "`Commands: " + ", ".join([key for key in data["code"]]) + "`"
            elif spl[1] == "tag":
                return "`Tags: " + ", ".join([key for key in data["tags"]]) + "`"
            elif spl[1] == "startup":
                return "`Startup code: " + ", ".join([key for key in data["startup"]]) + "`"
            else:
                return "`Invalid delete type, must be cmd, tag or startup`"
        elif spl[0] == "string":
            word = " ".join(spl[1:])

            seqs = get_seqs(word, is_number=False)

            digits = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            uword = word.upper()
            raw_freqs = {digit: int((uword.count(digit) / float(len(uword))) * 10000)/100 for digit in digits}
            top_digits = sorted(raw_freqs.items(), key=operator.itemgetter(1))[-10:][::-1]
            freqs = "; ".join(["%s: %s%s" % (digit[0], digit[1], "%") for digit in top_digits])

            sortword = "".join(sorted(word))
            return "```\n" + "\n".join([
                "Information about " + word + ":",
                "  -  Best sequence of repeating letters: " + seqs[2],
                "  -  Best sequence of rising letters: " + seqs[0],
                "  -  Best sequence of falling letters: " + seqs[1],
                "  -  " + seqs[3],
                "  -  Top 10 most frequent digits: " + freqs,
                "  -  The word sorted alphabetically: " + sortword
            ]) + "\n```"
        elif spl[0] == "number":
            n = int(spl[1])
            real_n = n
            strn = spl[1]
            negative = False
            if n < 0:
                negative = True
                n = abs(n)

            prime_factors = find_largest_prime(n)

            seqs = get_seqs(strn, is_number=True)

            square_line = "Is not a square number"
            if math.sqrt(n).is_integer():
                square_line = "Is " + str(int(math.sqrt(n))) + " squared"

            prime_line = "Is a prime number"
            if len(prime_factors) != 0:
                prime_line = "Prime factors: " + ", ".join([str(x) for x in prime_factors])

            neg_line = "Is not negative."
            if negative:
                strn = "-" + strn
                neg_line  = "Is negative"

            digits = "0123456789"
            freqs = [ "%s: %s%s" % (digit, str(int((strn.count(digit)/len(strn)) * 10000)/100), "%") for digit in digits ]


            sortstrn = "".join(sorted(strn))
            return "```\n" + "\n".join([
                "Information about " + strn + ":",
                "  -  Written as " + get_word(real_n),
                "  -  " + neg_line,
                "  -  " + prime_line,
                "  -  Best sequence of repeating digits: " + seqs[2],
                "  -  Best sequence of rising digits: " + seqs[0],
                "  -  Best sequence of falling digits: " + seqs[1],
                "  -  " + seqs[3],
                "  -  " + square_line,
                "  -  The sum of its digits is: " + str(seqs[4]),
                "  -  The frequences of the digits are: " + "; ".join(freqs),
                "  -  The number sorted lowest to highest: " + sortstrn
            ]) + "\n```"
        elif spl[0] == "startup":
            name = spl[1]
            code = [x for x in [y.replace("```", "").replace("`\\``", "```") for y in " ".join(spl[2:]).split("\n")] if x != "" and x != "py"]
            data["startup"][name] = code
            ret = yield from run_eval(code, ctx=ctx)
            save()
            return ret
        elif spl[0] in data["code"]:
            ret = yield from run_eval(data["code"][spl[0]], args=spl[1:], ctx=ctx)
            save()
            return ret
        return "`Invalid command`"
    elif cmd in data["tags"]:
        return data["tags"][cmd]
    else:
        return "`Invalid tag`"


@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

    if os.path.exists("selfbot.dat"):
        f = open("selfbot.dat")
        temp = json.load(f)
        if not f.closed:
            f.close()

        merge(data, temp)

    for name in data["startup"]:
        temp = yield from run_eval(data["startup"][name])


last_edit = ""


def process_message(message):
    global last_edit
    if message.author.id == client.user.id and message.id != last_edit:  # is me
        text = message.content
        print(text)
        changed = False
        c_open = data["open"]
        c_close = data["close"]
        index = text.find(c_open)
        while index > -1:
            if text[index - 1] == "\\":
                text = text[:index - 1] + text[index:]
                changed = True
                index = text.find(c_open, index + 3)
            else:
                nindex = text.find(c_close, index)
                if nindex > -1:
                    while nindex > -1 and text[nindex-1] == "\\":
                        text = text[:nindex-1] + text[nindex:]
                        nindex = text.find(c_close, nindex)
                    if nindex > -1:
                        cmd = text[index + 2:nindex]
                        ret = yield from run_command(cmd, ctx=message)
                        ntext = text[:index] + ret + text[nindex + 2:]
                        if len(ntext) > 1900:
                            ntext = text[:index] + "`{TOO LONG}`" + text[nindex + 2:]
                        text = ntext
                        changed = True
                        index = text.find(c_open, nindex)
        if changed:
            if text == "":
                yield from client.delete_message(message)
            else:
                try:
                    last_edit = message.id
                    yield from client.edit_message(message, text)
                except Exception:
                    yield from client.edit_message(message, "`::EDIT FAILED::` " + message.content)

@client.event
@asyncio.coroutine
def on_message(message):
    yield from process_message(message)


@client.event
@asyncio.coroutine
def on_message_edit(before, after):
    yield from process_message(after)


email = None
password = None
if not os.path.exists("credentials.txt"):
    print("Credentials not found, please enter them below:")
    email = input("EMAIL: ")
    password = input("PASSWORD: ")
    f = open("credentials.txt", "w")
    f.write(email + "\n")
    f.write(password)
    f.close()
    print("Credentials saved, logging in...")
else:
    print("Credentials found, logging in...")
    f = open("credentials.txt", "r")
    for line in f:
        if email is None:
            email = line.replace("\n", "")
        elif password is None:
            password = line.replace("\n", "")

if email is not None and password is not None:
    client.run(email, password)
else:
    print("Invalid credentials, please delete or fix credentials.txt")

