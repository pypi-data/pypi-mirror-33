class Comment(object):
    def __init__(self, content, start, end=None):
        self.content = content
        self.start = start
        self.end = start if end is None else end

    def __str__(self):
        lines = ['<Comment>']
        num = '%{0}d'.format('%d' % len(str(self.end)))
        for i, line in enumerate(self.content.split('\n')):
            lines.append('{0} | {1}'.format(num % (i + self.start), line))
        return '\n'.join(lines)

class CommentScanner(object):
    def __init__(self, tokens, debug=False):
        self.buffer = []
        self.tokens = tokens
        self.picked_token = None
        self.picked_line = None
        self.debug = debug

    def dump(self, end_line=None):
        comment = None
        if self.buffer:
            comment = '\n'.join(self.buffer)
            comment = Comment(comment, self.picked_line, end_line)
        self.buffer = []
        self.picked_line = None
        return comment

    def print_line_log(self, line, line_num, description=''):
        if not self.debug:
            return
        mark = '' if self.picked_line is None else 'X'
        print '%3d | %-80s | %s %s' % (line_num, line, mark, description)

    def scan_line_begin(self, line):
        for token in self.tokens:
            left_token = token if type(token) is str else token[0]
            start = line.find(left_token)
            if start >= 0:
                self.picked_token = token
                start += len(left_token)
                return start
        return -1

    def scan_line_end(self, line):
        if type(self.picked_token) is str:
            return len(line)
        return line.find(self.picked_token[1])

    def scan_line(self, line, line_num):
        start = 0
        content = line
        if self.picked_line is None:
            start = self.scan_line_begin(content)
            if start >= 0:
                content = content[start:]
                self.picked_line = line_num
                start = 0
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
        'c': ['//', ('/*', '*/')],
        'cpp': ['//', ('/*', '*/')],
        'javascript': ['//', ('/*', '*/')],
        'python': ['#', ('\'\'\'', '\'\'\''), ('\"\"\"', '\"\"\"')]
    }

    def __init__(self, language, debug=False):
        params = self.scanner_params.get(language)
        if params:
            self.scanner = CommentScanner(params, debug)

    def fetch(self, content):
        comments = []
        picked_comment = None
        for comment in self.scanner.scan(content):
            if not picked_comment:
                picked_comment = comment
                continue
            if picked_comment:
                if comment.start == picked_comment.end + 1:
                    picked_comment.end = comment.end
                    picked_comment.content += '\n' + comment.content
                    continue
                comments.append(picked_comment)
                picked_comment = None
            comments.append(comment)
        if picked_comment:
            comments.append(picked_comment)
        return comments

__version__ = '0.2.0'
