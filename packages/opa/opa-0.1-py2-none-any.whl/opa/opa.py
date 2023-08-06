import requests
import click
import re

@click.command()
@click.argument('url', nargs=1)

def cli(url):
  """ openQA parser """
  url = prepare_url(url)
  decision = job_state(url)
  parse_log(url)

def prepare_url(url):
  """Validate and prepare the URL of the test"""
  parsed = re.search(r'(http[s]*://.*)/tests/([0-9]*)[#|/]*.*', url)
  if parsed:
    click.echo('Detected test %s/tests/%s instance' % (parsed.group(2), parsed.group(1)) )
    return parsed.group(1)+'/tests/'+parsed.group(2)
  else:
    click.echo('The URL cannot be detected!')
    exit(1)

def job_state(url):
  """ Determine if the job waits, runs or finished """
  try:
    r = requests.get(url+'/status')
    if r.status_code == 200:
      state = r.json()['state']
      if state == 'done':
        decision = 'parse'
      else:
        decision = 'exit'
    else:
      state = 'unknown'
      decision = 'exit'
  except requests.exceptions.ReadTimeout as e:
    state = 'live'
    decision = 'exit'
  click.echo('The job is currently in %s state. Going to %s!' % ( state, decision ) )

def parse_log(url):
  r = requests.get(url+'/file/autoinst-log.txt')
  content = merge_lines(r.content.decode('utf-8'))
  content = content.split('\n')
  for line in content:
    line = re.search('^\[(.*)\] \[(.*)\] (.*)$', line)
    if line and line.group(3):
      time = re.sub(r"([0-9]+-[0-9]+-[0-9]+T)|\..*", "", line.group(1))
      seve = multiple_replace({"info": "I", "debug": "D"}, line.group(2))
      text = filter_text(line.group(3))
      if text:
        click.echo('%s %s' % (time, text))

def merge_lines(content):
  content = re.sub(r"mustmatch=\[\n", "mustmatch=[", content)
  content = re.sub(r"',\n", "',", content)
  content = re.sub(r"='\n", "='", content)
  content = re.sub(r"=\[\n", "=[", content)
  content = re.sub(r"\n],", "],", content)
  content = re.sub(' +', ' ', content)
  return content

def multiple_replace(adict, text):
  regex = re.compile("|".join(map(re.escape, adict.keys(  ))))
  return regex.sub(lambda match: adict[match.group(0)], text)

def filter_text(text):
  if not re.match("^(Routing to a callback|200 OK \(|GET \"/.*/isotovideo/status|MATCH\(|no match:|no change:|WARNING:|DEBUG_IO:)", text):
    text = re.sub(r"^(\|\||<<|>>)","", text)
    if not re.match("^(\||<|>)", text):
      text = "  "+text
    #text = multiple_replace({"||| ": "| ", ">>>": ">", "<<<": "<"}, text)
    return text

