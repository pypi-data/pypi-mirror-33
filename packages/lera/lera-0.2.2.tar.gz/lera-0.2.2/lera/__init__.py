r"""
https://lera.ai is a journal for your ML experiments. It has lightweight visualization and can store images, sounds, files, models, source code

Basic usage:
```python
lera.log_hyperparams({
    'title': 'MNIST classifier',
    'lr': lr
})
while step < total_steps:
    ...
    lera.log('loss', loss.data[0])
    if lera.every(seconds=60 * 5): # log every 5 minutes
        lera.log_image('sample', tensor)
```


To any of `log_` methods you can pass either one key-value or a dictionary of key-values:
```python
lera.log('loss', loss.data[0])

# Both works

lera.log({
    'loss': loss.data[0],
    'test_loss': test_loss.data[0]
})
```
There is a difference how those methods sends data:
* `log_hyperparams` - only first value is sent for a name.
* `log` - logs every value.
* `log_audio`, `log_image`, `log_file`, `log_data` - overwrites previous data sent with the same name.

"""
import sys
import os.path
import os
import time
import uuid
import json
import multiprocessing as mp
import atexit
import warnings
import inspect

session = uuid.uuid4().hex
machine = None
once = True
_enabled = True
_test = False
proc = None
site = os.environ.get("LR") or "https://lera.ai" 
chunk_list = mp.Manager().list()
session_file = os.path.expanduser('~/.lr')


if not os.path.exists(session_file):
  with open(session_file, "w") as sfile:
    sfile.write(uuid.uuid4().hex)


with open(session_file, "r") as sfile:
  machine=sfile.read()

def args2dict(name, value):
    args = {}
    if isinstance(name, dict): 
        args = name
    else:
        args[name] = value
    return args

def warn_wrong_type(filename, key, value):
    warnings.warn("lera.{} '{}' has wrong type {}".format(filename, key, type(value)))

def new_session(hyperparams=None):
    r"""
    Run in Jupyter notebooks to start a new experiment
    """
    global session
    session = uuid.uuid4().hex
    global hyper 
    hyper = {}
    global once
    once = True
    global chunk_list
    chunk_list = mp.Manager().list()
    global proc
    if proc is not None and proc.is_alive():
        proc.terminate()

    if hyperparams is not None:
        return log_hyperparams(hyperparams)

def sending_process(chunk_list):
  import requests
  import zlib
  PY3 = sys.version_info[0] == 3
  string_type = str if PY3 else unicode

  s = requests.Session()
  s.headers.update({
    'machine': machine, 
    })
  cur_chunk = {}
  finish = False
  cons_fails = 0

  bin_dict = {}
  try:
    while not finish:
      while len(chunk_list) > 0:
        arg_dict = {}
        args, now = chunk_list.pop(0) 
        if args is None:
          finish = True
          break
        if len(args) == 2:
          arg_dict[args[0]] = args[1]
        elif isinstance(args[0], dict): 
          arg_dict = args[0]
        else:
          raise Exception("wrong arguments")
        
        arg_dict_filter = {}
        for k, v in arg_dict.items():
          if isinstance(v, (bool, int, float, string_type)):
            arg_dict_filter[k] = v
          elif isinstance(v, list) and len([item for item in v if isinstance(item, (int, float))]) > 0: 
            arg_dict_filter[k] = v
          elif isinstance(v, (bytes, bytearray)):
              atype, aname = k.split(':')
              if atype == 'audio':
                  filename ="{}.wav".format(aname) 
                  bin_dict[aname] = (filename, v, "audio/wav")
                  arg_dict_filter[k] = filename
              elif atype == 'image':
                  filename ="{}.png".format(aname) 
                  bin_dict[aname] = (filename, v, "image/png")
                  arg_dict_filter[k] = filename
              elif atype == 'file':
                  bin_dict[aname] = (aname, v, "application/octet-stream")
                  arg_dict_filter[k] = aname
            
            
        arg_dict = arg_dict_filter

        for name in arg_dict:
          if not (name in cur_chunk):
            cur_chunk[name] = [(arg_dict[name], now)]
          else: 
            cur_chunk[name].append((arg_dict[name], now))

      if len(cur_chunk) > 0 or len(bin_dict) > 0:
        try:
          if len(bin_dict) > 0:
            r = s.post("{0}/data/{1}".format(site, session), files=bin_dict, timeout=5.0)
            bin_dict = {}
          if len(cur_chunk) > 0:
            r = s.post("{0}/data/{1}".format(site, session), data=json.dumps(cur_chunk), timeout=5.0, headers={ 'Content-Type' : 'application/octet-stream'})
            cur_chunk={}
          cons_fails = 0
        except Exception as e:
          cons_fails += 1
          print("lera.ai: error sending data", e)
          if cons_fails >= 6:
            print("lera.ai: Too many connection problems, stop sending.")
            finished = True
      if not finish:
        time.sleep(1)
  except: 
    e = sys.exc_info()[0]
    print("lera.ai error: ", e) 


def send(*args):
  if (not _enabled) or _test:
    return
  global once
  global proc
  if once:
    proc = mp.Process(target=sending_process, args=(chunk_list,))
    proc.start()
    once = False
    print("lera: open {} to view the progress".format(get_url())) 

  if proc.is_alive():
    chunk_list.append((args, time.time()))

hyper = {}

def log_hyperparams(name, value=None):
  r"""
  * `value (bool|int|float|str)` - hyperparam is logged one time.
  """
  args = args2dict(name, value)
  to_send = {}
  for name in args:
      if not (name in hyper):
        if isinstance(args[name], (bool, int, float, string_type)):
          hyper[name] = args[name]
          to_send[name] = args[name]
        else:
            warn_wrong_type('log_hyperparams', name, args[name])

  send(to_send)
  return to_send

steps = {}
ravg = {}
last_print = None 
to_print = {}
PY3 = sys.version_info[0] == 3
string_type = str if PY3 else unicode #basestring

# every_step=1000
# every_sec=1.2
# print=True

def log(name, value = None, console=False, average=0):
    r"""
    * `value (float|int|numpy.ndarray)` - any object that has `mean` and `std` methods. The later logs a pair of `mean` and `std`
    * `console` - print values to console. 

    PyTorch example:
    ```python
    lera.log('loss', loss.data[0], print=True)
    lera.log({ 
       'loss': loss.data[0],
       'layer1_output': output.data  # logs mean and std
    })
    ```
    """
    global steps
    global last_print

    args = args2dict(name, value)

    to_send = {}
    akey = None
    for k, v in args.items():
        akey = k

        steps[k] = steps[k] + 1 if k in steps else 0
        if isinstance(v, float):
            ravg[k] = ravg[k] * average + (1 - average) * v if k in ravg else v

        if isinstance(v, bool):
            warn_wrong_type('log', k, v)
        elif isinstance(v, (int, float)):
            to_send[k] = v
        elif getattr(v, 'mean', None) is not None and getattr(v, 'std', None) is not None:
            to_send[k] = [v.mean(), v.std()]
            #v = v.reshape((v.size,))
            #v.sort(kind='mergesort')
            #nargs[k] = v[::(v.size // 5)].tolist()
        else:
            warn_wrong_type('log', k, v)

    if _enabled:
        send(to_send)

    if console and akey is not None:
        now = time.time()
        delta = 1.0 #kwargs['console'] if isinstance(kwargs['console'], float) else 1.0
        if last_print is None:
            last_print = now
        for k, v in args.items():
            if isinstance(v, (int, float)):
                to_print[k] = ravg[k] if k in ravg else v
        if now - last_print > delta:
            last_print = now
            output = ["step: {step}"]
            to_print['step'] = None
            for k, v in to_print.items():
                if isinstance(v, int):
                    output.append("{0}: {1}{0}{2}".format(k, '{', '}'))
                elif isinstance(v, float):
                    output.append("{0}: {1}{0}:.4g{2}".format(k, '{', '}'))

            to_print['step'] = steps[akey]
            if len(output) > 7:
                output = '\n'.join(output)
            else:
                output = ', '.join(output)
            print(output.format(**to_print))
            #to_print = {}
    return to_send

def log_file(*filenames):
    r"""
    * `*filenames` - list of files to log. It may be source code files or binary files.
    
    For the source code you then can see diff with previous versions.

    To log currently executing file:
    ```python
    lera.log_file(__file __)
    ```

    """
    if not _enabled: 
        return
    to_send = {}
    for filename in filenames:
        try:
            st = os.stat(filename)
            #print(st)
            if st.st_size > 1e+8:
                print("lera: this file is too big to send (> 100mb) {}", filename)
                continue
            
            to_send[os.path.basename(filename)] = open(filename, 'rb').read()
        except FileNotFoundError:
            print("lera: file not found {}".format(filename))
    log_data(to_send)
    return to_send

def log_data(name, value=None):
    r"""
    * `value (bytearray|bytes)` - bytes to send
    """
    if not _enabled: 
        return
    to_send = {}
    args = args2dict(name, value)
    for k, v in args.items():
        if isinstance(v, (bytes, bytearray)):
            to_send["file:{}".format(k)] = v
        else:
            warn_wrong_type('log_data', k, v)
    send(to_send)
    return to_send 

def log_audio(name, value=None, sample_rate=16000, clip=(-1, 1)):
    r"""
    * `value` - 1D numpy array with samples. Only mono is supported right now.
    * `sample_rate` - sample rate of the sound.
    * `clip` - clip values of a tensor, then scale and shift to (-1, 1) range.
    """
    if not _enabled: 
        return

    args = args2dict(name, value) 
    import numpy as np
    import io
    import wave

    to_send = {}
    for name, tensor in args.items():
        if not isinstance(tensor, np.ndarray):
            warn_wrong_type('log_audio', name, tensor)
            continue

        tensor = tensor.squeeze()
        if tensor.ndim != 1:
            warnings.warn("lera.log_audio '{}' tensor must have 1 dimention".format(name))
            continue

        if clip is not None:
            tensor = tensor.clip(clip[0], clip[1]) - clip[0]
            tensor = 2 * tensor / (clip[1] - clip[0]) - 1

        tensor *= (2 ** 15)
        tensor = tensor.astype('<i2')

        fio = io.BytesIO()
        write = wave.open(fio, 'wb')
        write.setnchannels(1)
        write.setsampwidth(2)
        write.setframerate(sample_rate)
        write.writeframes(tensor.tobytes())
        write.close()
        audio_string = fio.getvalue()
        fio.close()
        to_send["audio:{}".format(name)] = audio_string

    send(to_send)
    return to_send

def log_image(name, value=None, clip=(-1, 1)):
    r"""
    * `value` - either numpy tensor of shape (w, h, 3) or a PIL image
    * `clip` - clip values of tensor, then scale & shift to (0, 1) range.
    """
    if not _enabled: 
        return

    args = args2dict(name, value)

    import numpy as np
    from PIL import Image
    import io

    to_send = {}
    for name, img in args.items():
        if isinstance(img, np.ndarray):
            tensor = img
            assert(tensor.ndim == 3), 'input tensor should be 3 dimensional.'
            assert(tensor.shape[2] == 3), 'input tensor should be of (n, m, 3) shape.'
            #clip and -> [0, 1]
            if clip is not None:
                tensor = tensor.clip(clip[0], clip[1]) - clip[0]
                tensor = tensor / (clip[1] - clip[0])
            tensor *= 255
            img = Image.fromarray(tensor.astype('uint8').transpose(1, 0, 2), 'RGB')
        elif isinstance(img, Image.Image):
            pass
        else:
            warn_wrong_type('log_image', name, img)
            continue
        fio = io.BytesIO()
        img.save(fio, format='PNG')
        to_send["image:{}".format(name)] = fio.getvalue()
        fio.close()

    send(to_send)
    return to_send

exit_code = None
exit_exc = None
original_exit = sys.exit
original_exc = sys.excepthook

def exc_handler(exc_type, exc, *args):
  global exit_exc
  exit_exc = exc_type
  if original_exc is not None:
    original_exc(exc_type, exc, *args)

def my_exit(code=0):
    global exit_code
    exit_code = code
    original_exit(code)

sys.exit = my_exit
sys.excepthook = exc_handler

def on_exit():
  if proc is None:
    return

  if exit_exc is None and exit_code == 0:
    proc.join()
  else:
    proc.terminate()

def test(value):
    global _test
    _test = value

def enabled(value):
  r"""
    * `value (bool)` - Enable or disable logging. Put it before any other log statements
  """
  global _enabled
  _enabled = value

total_run = {}
last_run = {}

def every(**kwargs):
    r"""
    Used with `if` within training loop to check if number of steps or seconds passed since last execution.
    
    ```python
    if lera.every(steps=1000):
        # do some time consuming inference to make a sample
        lera.log_audio('sample', sound_tensor)

    if lera.every(seconds=1):
        # friendly printing every second
        print("step: {}, loss: {}".format(step, loss.data[0]))
    ```
    """
    assert ('steps' in kwargs or 'seconds' in kwargs), "Ether steps or seconds must be specified"

    frame = inspect.currentframe()
    outer_frame = inspect.getouterframes(frame)[1]
    filename = outer_frame['filename'] if 'filename' in outer_frame else outer_frame[1]
    lineno = outer_frame['lineno'] if 'lineno' in outer_frame else outer_frame[2]
    result = False
    try:
        key = "{}_{}".format(filename, lineno)
        if 'steps' in kwargs:
            if key not in total_run:
                total_run[key] = 0
            total_run[key] += 1
            if key not in last_run or total_run[key] - last_run[key] >= kwargs['steps']  :
                last_run[key] = total_run[key]
                result = True
        elif 'seconds' in kwargs:
            now = time.time()
            if key not in last_run or now - last_run[key] >= kwargs['seconds']  :
                last_run[key] = now
                result = True
    finally:
        del frame
        del outer_frame
    return result

def get_url(): 
  r"""
    Get an URL to access your session list
  """
  return "{0}/m/{1}".format(site, machine[:6])

def main():
  print("Open {} to view expriments that run from this box".format(get_url())) 

if not _test:
    atexit.register(on_exit)
__all__ = ['log_hyperparams', 'log', 'log_audio', 'log_image', 'log_file', 'log_data', 'new_session', 'every', 'enabled', 'get_url', ]
