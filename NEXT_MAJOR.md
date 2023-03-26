# Changes queued for next marjor version
These are changes identified as needed but deferred to the next bumped major version. The reason is that some of the changes here introduce a breaking change that per see can't be defended as needed (maybe just aestethincs) but once they are accummulated makes sense to bump a major version.

## 1. Rename `Logger.getLogger()` to `Logger.get_logger()`
As it was one of the initial classes in this package, it got inspired by the official `logging.getLogger()`. After some time I realized that it causes sometimes confusion (_is it the official one or the one from my package?_) and also I do try to implement [the Python conventions](https://peps.python.org/pep-0008/#method-names-and-instance-variables) everyehere.