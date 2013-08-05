# -*- coding: utf-8 -*-

"""Provides a ``join_to_transaction`` function which adds a function call,
  with args / kwargs, as an after commit hook.
"""

import logging
logger = logging.getLogger(__name__)

import threading
import transaction

def _handle_commit(tx_succeeded, *args_list, **kwargs):
    """Handle a successful commit by calling the callable registered as an after
      commit hook.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_callable = Mock()
          >>> mock_args_list = [mock_callable, 'a', 'b']
      
      If the transaction didn't succeed, it's a noop::
      
          >>> _handle_commit(False)
          >>> mock_callable.called = False
      
      If ``tx_succeeded`` is callable, treats the ``args_list`` as the remaining args::
      
          >>> _handle_commit(mock_callable, *mock_args_list[1:], foo='bar')
          >>> mock_callable.assert_called_with('a', 'b', foo='bar')
      
      Otherwise treats the first item in the ``args_list`` as the callable
      and calls it with the remaining args and the kwargs::
      
          >>> _handle_commit(True, *mock_args_list, foo='bar')
          >>> mock_callable.assert_called_with('a', 'b', foo='bar')
      
    """
    
    # If in debug mode, show what's going on under the hood.
    log_args = (tx_succeeded, args_list, kwargs)
    logger.debug('handle_commit: {0} for {1} {2}'.format(*log_args))
    
    # If the transaction failed, return.
    if tx_succeeded is False:
        return
    
    # Otherwise, if the first arg to this function is a callable,
    # this function was trigged by a before commit hook, so unpack accordingly.
    if callable(tx_succeeded):
        callable_ = tx_succeeded
        args = args_list
    else: # this came from an after commit hook so again unpack accordingly.
        callable_ = args_list[0]
        args = args_list[1:]
    
    # Call the callable with the unpacked args and kwargs.
    callable_(*args, **kwargs)

def _join_to_transaction(when, callable_, *args, **kwargs):
    """Add an after commit hook to the current transaction to call 
      ``callable_(*args, **kwargs)`` iff the current transaction succeeds.
      
      Setup::
      
          >>> from mock import Mock
          >>> import transaction
          >>> _original_get = transaction.get
          >>> transaction.get = Mock()
          >>> mock_tx = Mock()
          >>> transaction.get.return_value = mock_tx
      
      Add an after commit hook to the current transaction::
      
          >>> _join_to_transaction('after', 'callable', 'a', 'b', foo='bar')
          >>> mock_tx.addAfterCommitHook.assert_called_with(_handle_commit, 
          ...         args=['callable', 'a', 'b'], kws={'foo': 'bar'})
      
      Add a before commit hook::
      
          >>> mock_tx = Mock()
          >>> transaction.get.return_value = mock_tx
          >>> _join_to_transaction('before', 'callable', 'a', 'b', foo='bar')
          >>> mock_tx.addBeforeCommitHook.assert_called_with(_handle_commit, 
          ...         args=['callable', 'a', 'b'], kws={'foo': 'bar'})
      
      Note that ``'after'`` and ``'before'`` are the only ``when`` values currently
      implemented::
      
          >>> _join_to_transaction('foo', 'callable', 'a', 'b', foo='bar')
          Traceback (most recent call last):
          ...
          NotImplementedError
      
      Teardown::
      
          >>> transaction.get = _original_get
      
    """
    
    # If in debug mode, show what's going on under the hood.
    log_args = (callable_, args, kwargs)
    logger.debug('join_to_transaction: {0} {1} {2}'.format(*log_args))
    
    # Build a args list of [callable_, *args]
    args_list = [callable_]
    args_list.extend(args)
    
    # Add an after or before commit hook.
    current_tx = transaction.get()
    if when == 'before':
        method_name = 'addBeforeCommitHook'
    elif when == 'after':
        method_name = 'addAfterCommitHook'
    else:
        raise NotImplementedError
    method = getattr(current_tx, method_name)
    method(_handle_commit, args=args_list, kws=kwargs)


def join_before_transaction(callable_, *args, **kwargs):
    """Call ``callable_(*args, **kwargs)`` before the current transaction commits.
      
      Setup::
      
          >>> from mock import Mock
          >>> from pyramid_weblayer import tx
          >>> _original = tx._join_to_transaction
          >>> tx._join_to_transaction = Mock()
          >>> tx._join_to_transaction.return_value = None
      
      Test::
      
          >>> join_before_transaction('func', 'arg', kw='')
          >>> tx._join_to_transaction.assert_called_with('before', 'func', 'arg', kw='')
      
      Teardown::
      
          >>> tx._join_to_transaction = _original
      
    """
    
    return _join_to_transaction('before', callable_, *args, **kwargs)

def join_after_transaction(callable_, *args, **kwargs):
    """Call ``callable_(*args, **kwargs)`` after the current transaction commits.
      
      Setup::
      
          >>> from mock import Mock
          >>> from pyramid_weblayer import tx
          >>> _original = tx._join_to_transaction
          >>> tx._join_to_transaction = Mock()
          >>> tx._join_to_transaction.return_value = None
      
      Test::
      
          >>> join_after_transaction('func', 'arg', kw='')
          >>> tx._join_to_transaction.assert_called_with('after', 'func', 'arg', kw='')
      
      Teardown::
      
          >>> tx._join_to_transaction = _original
      
    """
    
    return _join_to_transaction('after', callable_, *args, **kwargs)


# Default the main ``join_to_transaction`` to use an after commit hook.
join_to_transaction = join_after_transaction

def call_in_background(target, args=None, kwargs=None, join=None, thread_cls=None):
    """Helper function for the common use case of firing and forgetting a
      function call in a background thread.
    """
    
    # Compose.
    if join is None:
        join = join_to_transaction
    if thread_cls is None:
        thread_cls = threading.Thread
    
    thread_kwargs = {}
    if args is not None:
        thread_kwargs['args'] = args
    if kwargs is not None:
        thread_kwargs['kwargs'] = kwargs
    thread = thread_cls(target=target, **thread_kwargs)
    return join(thread.start)

