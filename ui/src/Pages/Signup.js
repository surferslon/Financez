export default function Login() {

  return (
    <div class="frame">
        <div class="frame-header">Financez</div>

        <form class="auth-form" method="post">
            {% csrf_token %}
            <input  type="hidden" name="next" value="{{ next }}" />
            {{ form.username }}
            {{ form.password1 }}
            {{ form.password2 }}
            <button type="submit" value="Register">{% trans 'Done' %}</button>
            <div class='error-list'>
            {% for field, error in form.errors.items %}
                {{ error }}
                </br>
            {% endfor %}
        </div>
        </form>

    </div>

    <div class="frame signup-frame">
        <span>{% trans "Have an account?" %}</span>
        <a href="{% url 'login' %}">{% trans 'Log in' %}</a>
    </div>

  )

}
