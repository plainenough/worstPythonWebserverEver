#!/usr/bin/env python
def main(error):
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)
    return Errornator(error)


def Errornator(error):
    import random
    errors = [
        'Awwwww Bukkits.',
        'Turbo-NO-Bueno.',
        'Saving face is for the weak.',
        '(∩ ͡° ͜ʖ ͡°)⊃━☆ﾟ. * ・ ｡ﾟ Copypastus Totalus!!',
        'Defensive Programming, also for the weak.',
        "If you're gonna be dumb you gotta be tough.",
        "It's not my data.",
        'We have a guy for that.',
        'The answer is not 42!',
        "Yo've been robbed!",
        'You probably need to run it through fuckit.py.',
        'If we could hit that bullseye the rest of the dominos will fall like
        a house of cards. Checkmate?',
        "Why don't you try that command again with a --suck-less option?",
        'Yeah that was made of suck!',
        "Good thing I caught that, windows would have bluescreened.",
        'HPFM',
        """"TypeError: 'str' object does not support item assignment”""",
        'Bad joke Tuesday.',
        '<Something useful here>',
        'His name was Robert Paulsen.',
        'This problem is bigger in Texas.',
        'Rebooting the sever....',
        "D'oh!",
        'Release the Kraken!',
        "I'm really happy for you, I'ma let you finish but.....",
        "I get what yo're saying.",
        'Its on these big guys.',
        "I'm going to get you a list of all of the mess ups.",
        'Lets tighten up your list.',
        'Do you want a cookie?',
        'Or not....',
        "We don't have process for this.",
        'Giggity',
        'Gotta hit that like a caveman.',
        'I sent you an email already, what more do you want?',
        "It can't be that hard.",
        'We are still in need of more data.',
        'Required to make you mad.',
        "If you pay me, I'll deliver your error."
        ]
    trash = error
    return random.choice(errors)


if __name__ == '__main__':
    print(main('string'))
