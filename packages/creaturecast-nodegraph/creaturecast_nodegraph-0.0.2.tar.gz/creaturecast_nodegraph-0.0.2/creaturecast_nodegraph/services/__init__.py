library_url = 'http://creaturecast-library.herokuapp.com'
#library_url = 'http://127.0.0.1:5000'

def split_by_lines(text_generator):

    last_line = ""
    try:
        while True:
             chunk = "%s%s" % (last_line, next(text_generator))
             chunk_by_line = chunk.split('\n')
             last_line = chunk_by_line.pop()
             for line in chunk_by_line:
                 yield line

    except StopIteration: # the other end of the pipe is empty
        yield last_line
        raise StopIteration
