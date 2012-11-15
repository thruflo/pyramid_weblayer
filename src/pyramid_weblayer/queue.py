# -*- coding: utf-8 -*-

"""Provides a ``QueueProcessor`` utility that consumes and processes data
  from one or more redis channels.
  
      >>> redis_client = '<redis.Redis> instance'
      >>> input_channels = ['channel1', 'channeln']
      >>> handle_data = lambda data_str: data_str
      >>> processor = QueueProcessor(redis_client, input_channels, handle_data)
  
  Run in the main / current thread::
  
      >>> # processor.start()
  
  Run in a background thread::
      
      >>> # processor.start(async=True)
      
  If running in a background thread, call ``stop()`` to exit::
  
      >>> # processor.stop()
  
  If you want jobs to be requeued (at the back of the queue)
  This provides a very simple inter-process messaging and / or background
  task processing mechanism.  Queued messages / jobs are explictly passed
  as string messages.  
  
  Pro: you're always in control of your code execution environment.
  Con: you have to deal with potentially tedious message parsing.
"""

import logging
logger = logging.getLogger(__name__)

import json
import threading
import time

class QueueProcessor(object):
    """Consume data from a redis queue.  When it arrives, pass it to
      ``self.handler_function``.
    """
    
    running = False
    
    def stop(self):
        """Call ``stop()`` to stop processing the queue the next time a job is
          processed or the input queue timeout is reached.
        """
        
        logger.info('QueueProcessor.stop()')
        
        self.running = False
    
    def _start(self):
        """Actually start processing the input queue(s) ad-infinitum."""
        
        logger.info('QueueProcessor.start()')
        logger.info(self.channels)
        
        self.running = True
        while self.running:
            logger.debug(('QueueProcessor reconnecting', self.channels))
            try:
                return_value = self.redis.blpop(self.channels, timeout=self.timeout)
            except Exception as err:
                logger.warn(err, exc_info=True)
                time.sleep(self.timeout)
            else:
                logger.debug(('QueueProcessor return value obtained', self.channels))
                if return_value is not None:
                    channel, body = return_value
                    try:
                        self.handle_function(body)
                    except Exception as err:
                        logger.warn(err, exc_info=True)
                        logger.warn(return_value)
                        if self.should_requeue:
                            self.redis.rpush(channel, body)
                if self.reconnect_delay:
                    time.sleep(self.reconnect_delay)
    
    def start(self, async=False):
        """Either start running or start running in a thread."""
        
        if self.running:
            return
        
        if async:
            threading.Thread(target=self._start).start()
        else:
            self._start()
    
    def __init__(self, redis_client, channels, handle_function, timeout=20,
            reconnect_delay=0.005, should_requeue=False):
        """Instantiate a queue processor::
          
              >>> processor = QueueProcessor(None, None, None)
          
        """
        
        self.redis = redis_client
        self.channels = channels
        self.handle_function = handle_function
        self.timeout = timeout
        self.reconnect_delay = reconnect_delay
        self.should_requeue = should_requeue
    

