import logging

import flask
from flask.views import MethodView

from packy_agent.control_server.forms.activate import ActivateForm
from packy_agent.control_server.forms.activate_extra import ActivateExtraForm
from packy_agent.control_server.views.base import smart_redirect
from packy_agent.exceptions import AuthenticationError, ValidationError
from packy_agent.managers.install_and_upgrade import install_and_upgrade_manager
from packy_agent.utils.auth import set_authentication_cookie, is_activated
from packy_agent.utils.misc import get_inactive_agents

logger = logging.getLogger(__name__)


class ActivateView(MethodView):

    def get(self):
        if is_activated():
            return flask.redirect(flask.url_for('index'))

        return flask.render_template('activate.html', form=ActivateForm())

    def post(self):
        if is_activated():
            return flask.redirect(flask.url_for('index'))

        form = ActivateForm()
        if form.validate():
            email = form.email.data
            password = form.password.data

            try:
                agent_id = None
                agents = get_inactive_agents(email, password)
                if agents:
                    form = ActivateExtraForm(email=email, password=password)
                    agent_choices = tuple((str(id_), name) for id_, name in agents.iteritems())
                    form.agent.choices += agent_choices

                    if form.validate():
                        if form.agent.data != 'new':
                            agent_id = int(form.agent.data)
                            if agent_id not in agents:
                                flask.flash('Invalid agent')
                                return flask.redirect(flask.url_for('activation_failure'))
                    elif form.extra.data == 'yes':
                        return flask.render_template('activate_extra.html', form=form)
                    else:
                        form = ActivateExtraForm(email=email, password=password)
                        form.agent.choices += agent_choices
                        return flask.render_template('activate_extra.html', form=form)

                install_and_upgrade_manager.activate(email, password, agent_id=agent_id)

            except AuthenticationError:
                flask.flash('Not authenticated (invalid credentials)')
                return flask.redirect(flask.url_for('activation_failure'))
            except ValidationError as ex:
                flask.flash(ex.message)
                return flask.redirect(flask.url_for('activation_failure'))
            except Exception:
                logger.exception('Error during activation')
                flask.flash('Error during activation')
                return flask.redirect(flask.url_for('activation_failure'))

            set_authentication_cookie()
            return smart_redirect('success', 'index', button_text='Continue')

        return flask.render_template('activate.html', form=form)


class ActivationFailureView(MethodView):

    def get(self):
        return flask.render_template('activation_failure.html')
