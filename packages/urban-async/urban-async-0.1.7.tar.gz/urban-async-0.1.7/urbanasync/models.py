"""
Copyright (c) 2017 kwugfighter

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class Term:

    def __init__(self, data):
        self.data = data
        self.tags = data['tags']
        self.result_type = data['result_type']
        self.sound_urls = data['sounds']
        self.definitions = [self.Definition(definition) for definition in self.data['list']]


    def __repr__(self):
        return "<Term>"

    class Definition:

        def __init__(self, data):
            self.definition = data['definition']
            self.permalink = data['permalink']
            self.upvotes = data['thumbs_up']
            self.downvotes = data['thumbs_down']
            self.author = data['author']
            self.id = data['defid']
            self.word = data['word']
            self.example = data['example']

        def __repr__(self):
            return "<Definition of {}>".format(self.word)

        def __str__(self):
            return self.word