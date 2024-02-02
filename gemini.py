from os.path import exists
import re

INDEX_TEMPLATE = '''# My Gemini Capsule
Hello Geminauts!
## Latest posts:
## Tags
## Contact
=> mailto:hello@example.com
'''

GMI_EXTENSION = '.gmi'
TAGS_START = '(tags: '

def safe_read(path):
  if exists(path):
    f = open(path, 'r')
    return f.readlines()
  return []

def parse_post_link(link):
  '''Parses a line of text with this format or returns None if it is not in this format
  => gemini://example.com/posts/2024-02-02-post-title.gmi Post Title (tags: topic1, topic2)
  '''
  p = re.compile('=> .*/posts/[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z-]+\.gmi .* \(tags: [a-z0-9-, ]+')
  if p.match(link):
    date_and_slug = link[link.find('/posts/')+len('/posts/'):link.find(GMI_EXTENSION)]
    date = date_and_slug[:10]
    slug = date_and_slug[11:]
    title = link[link.find(GMI_EXTENSION)+len(GMI_EXTENSION):link.find(TAGS_START)].strip()
    tags = link[link.find(TAGS_START)+len(TAGS_START):-1].split(', ') #TODO fix bug in final tag
    return Post(date, slug, title, tags)
  return None

class Capsule:
  def __init__(self, root, url):
    self.root = root
    self.url = url
    self.new_posts = []
    lines = safe_read('{root}/index.gmi'.format(root=self.root))
    if not lines:
      lines = INDEX_TEMPLATE.split('\n')
    self.index = Index(lines)

  def new_post(self, post):
    self.new_posts.append(post)
    self.index.new_post(post)

class Index:
  def __init__(self, lines):
    self.lines = lines
    self.latest_posts = []
    for line in lines:
      post = parse_post_link(line)
      if post:
        self.latest_posts.insert(0, post)
      # TODO initialize tags
      # 

  def new_post(self, post):
    self.latest_posts.insert(0, post)
    # TODO update tags

class Post:
  def __init__(self, date, slug, title, tags, content=None):
    self.date = date
    self.slug = slug
    self.title = title
    self.tags = tags
    self.content = content
