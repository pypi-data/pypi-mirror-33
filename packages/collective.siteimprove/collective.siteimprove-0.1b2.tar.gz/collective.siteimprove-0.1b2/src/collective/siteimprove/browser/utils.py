from AccessControl.PermissionRole import rolesForPermissionOn
from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView


class AnonCanView(BrowserView):
    """Returns true if anonymous user can view content"""

    def __call__(self):
        """Can we see this"""
        return 'Anonymous' in rolesForPermissionOn('View', self.context)


class UseDomainView(BrowserView):
    """  Returns true if the domain function is to be used in the
         siteimprove js header false implies that input function will
         be used instead
    """

    def __call__(self):
        # figure out if domain or input function should be used
        context_state = queryMultiAdapter((self.context, self.request),
                                          name=u'plone_context_state')
        if context_state is not None:
            return context_state.is_portal_root()  # True = domain function
        return False  # False = input function
