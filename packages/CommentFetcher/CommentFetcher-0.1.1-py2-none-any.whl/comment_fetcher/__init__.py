class Comment(object):
    def __init__(self, content, start, end=None):
        self.content = content
        self.start = start
        self.end = start if end is None else end

    def __repr__(self):
        return '<Comment start={0} end={1} length={2}>'\
            .format(self.start, self.end, len(self.content))

class CommentScanner(object):
    def __init__(self, token, line_token, debug=False):
        self.buffer = []
        self.token = token
        self.line_token = line_token
        self.is_multiple = False
        self.picked_line = None
        self.debug = debug

    def dump(self, end_line=None):
        comment = None
        if self.buffer:
            comment = Comment(''.join(self.buffer), self.picked_line, end_line)
        self.buffer = []
        self.picked_line = None
        return comment

    def print_line_log(self, line, i, description=''):
        if not self.debug:
            return
        mark = '' if self.picked_line is None else 'X'
        print '%2d | %-80s | %s %s' % (i, line, mark, description)

    def scan_line_begin(self, line):
        start = line.find(self.token[0])
        line_start = line.find(self.line_token)
        if line_start >= 0:
            if start >= 0 and start < line_start:
                self.is_multiple = True
                start += len(self.token[0])
            else:
                self.is_multiple = False
                start = line_start + len(self.line_token)
        elif start >= 0:
            self.is_multiple = True
            start += len(self.token[0])
        return start

    def scan_line_end(self, line):
        return line.find(self.token[1]) 

    def scan_line(self, line, line_num):
        start = 0
        content = line
        if self.picked_line is None:
            start = self.scan_line_begin(content)
            if start >= 0:
                content = content[start:]
                self.picked_line = line_num
                if not self.is_multiple:
                    self.buffer.append(content)
                    self.print_line_log(line, line_num)
                    return self.dump()
            else:
                self.print_line_log(line, line_num)
                return None
        end = self.scan_line_end(content)
        self.print_line_log(line, line_num)
        if end >= 0:
            self.buffer.append(content[start:end])
            return self.dump(line_num)
        self.buffer.append(content[start:])
        return None

    def scan(self, content):
        comments = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            comment = self.scan_line(line, i)
            if comment:
                comments.append(comment)
        comment = self.dump(len(lines) - 1)
        if comment:
                comments.append(comment)
        return comments

class CommentFetcher(object):
    scanner_params = {
        'c': [('/*', '*/'), '//'],
        'cpp': [('/*', '*/'), '//'],
        'javascript': [('/*', '*/'), '//'],
        'python': [('\'\'\'', '\'\'\''), '#']
    }

    def __init__(self, language, debug=False):
        params = self.scanner_params.get(language)
        if params:
            self.scanner = CommentScanner(params[0], params[1], debug)

    def fetch(self, content):
        return self.scanner.scan(content)

__version__ = '0.1.1'
