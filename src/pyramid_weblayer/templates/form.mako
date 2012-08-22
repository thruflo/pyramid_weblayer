<%def name="field(renderer, field_type, name, label=None, help=None, 
        help_position='inline', required=False, **kwargs)">
  <div class="control-group ${name}-control ${renderer.is_error(name) and 'error' or ''}">
    % if label is not False:
      <%
        if label is None:
            label = name.replace('_', ' ').replace('-', ' ').title()
        if not label.endswith(':'):
            label += ':'
      %>
      <label class="control-label" for="${name}">
        ${label}
        % if required:
          <span class="required">*</span>
        % endif
      </label>
    % endif
    <div class="controls">
      ${getattr(renderer, field_type)(name, **kwargs)}
      <span class="help help-${help_position}">
        % if help:
          ${help}
        % endif
        <span class="field-error">
          % if renderer.errors_for(name):
            % for error_message in renderer.errors_for(name):
              ${error_message}
            % endfor
          % endif
        </span>
      </span>
    </div>
  </div>
</%def>
