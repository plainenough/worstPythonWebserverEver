#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This will need to UTF really really Hard.
import sys
import codecs
import random

def Errornator(error):
    errors = [u'Awwwww Bukkits.', 
            u'Turbo-NO-Bueno.', 
            u'Saving face is for the weak.', 
            u'(∩ ͡° ͜ʖ ͡°)⊃━☆ﾟ. * ・ ｡ﾟ Copypastus Totalus!!', 
            u'Defensive Programming, also for the weak.', 
            u"If you're gonna be dumb you gotta be tough.", 
            u"It's not my data.", 
            u'We have a guy for that.',
            u'The answer is not 42!',
            u"You've been robbed!",
            u'You probably need to run it through fuckit.py.',
            u'If we could hit that bullseye the rest of the dominos will fall like a house of cards. Checkmate?',
            u"Why don't you try that command again with a --suck-less option?",
            u'Yeah that was made of suck!',
            u"Good thing I caught that, windows would have bluescreened.",
            u'HPFM',
            u""""TypeError: 'str' object does not support item assignment”""",
            u'Bad joke Tuesday.',
            u'<Something useful here>',
            u'His name was Robert Paulsen.',
            u'This problem is bigger in Texas.',
            u'Rebooting the sever....',
            u"D'oh!",
            u'Release the Kraken!',
            u"I'm really happy for you, I'ma let you finish but.....",
            u"I get what you're saying.",
            u'Its on these big guys.',
            u"I'm going to get you a list of all of the mess ups.",
            u'Lets tighten up your list.',
            u'Do you want a cookie?',
            u'Or not....',
            u"We don't have process for this.",
            u'Giggity',
            u'Gotta hit that like a caveman.',
            u'I sent you an email already, what more do you want?',
            u"It can't be that hard.",
            u'We are still in need of more data.',
            u'http://www.loser.com ---> make your day, visit this link, ignore this error.',
            u'Required to make you mad.',
            u"If you pay me, I'll deliver your error."
            ] 
    trash = error
    return random.choice(errors)


def main(error):
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)
    return Errornator(error)

if __name__ == '__main__':
    print(main(u'string'))
