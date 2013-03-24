<%def name="field(renderer, field_type, name, label=None, help=None,
        help_position='inline', required=False, add_on=None, add_on_position='prepend',
        extra_markup=None,**kwargs)">
  <div class="control-group ${name}-control ${renderer.is_error(name) and 'error' or ''}">
    % if label is not False:
      <%
        if label is None:
            label = name.replace('_', ' ').replace('-', ' ').title()
      %>
      <label class="control-label" for="${name}">
        % if required:
          ${label}<span class="required">*</span>
        % else:
          ${label}
        % endif
      </label>
    % endif
    <div class="controls ${'input-{0}'.format(add_on_position) if add_on else ''}">
      % if add_on is not None:
        <span class="add-on">${add_on | n}</span>
      % endif
      ${getattr(renderer, field_type)(name, **kwargs)}
      % if extra_markup:
        ${extra_markup | n}
      % endif
      <div class="help help-${help_position}">
        % if help:
          ${help}
        % endif
        <div class="field-error">
          % if renderer.errors_for(name):
            % for error_message in renderer.errors_for(name):
              ${error_message}.
            % endfor
          % endif
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="fileupload(renderer, name, config_str, exists=False, new_image=None,
        exists_image=None, label=None, help=None, help_position='inline', 
        required=False, thumbnail_class='', should_clear_above_help=False, 
        **kwargs)">
  <div class="control-group ${name}-control ${renderer.is_error(name) and 'error' or ''}">
    % if label is not False:
      <%
        if label is None:
            label = name.replace('_', ' ').replace('-', ' ').title()
      %>
      <label class="control-label" for="${name}">
        % if required:
          ${label}<span class="required">*</span>
        % else:
          ${label}
        % endif
      </label>
    % endif
    <div class="controls">
      <input type="hidden" name="params" value="${config_str}" />
      <%
        suffix = 'exists' if exists else 'new'
      %>
      <div class="fileupload fileupload-${suffix}" data-provides="fileupload">
        <div class="fileupload-new thumbnail ${thumbnail_class}">
          <img src="${new_image}" />
        </div>
        <div class="fileupload-preview fileupload-exists thumbnail ${thumbnail_class}">
          % if exists:
            <img src="${exists_image}" />
          % endif
        </div>
        <div>
          <span class="btn btn-file">
            <span class="fileupload-new">Choose an image</span>
            <span class="fileupload-exists">Change image</span>
            <input type="file" name="${name}" class="${kwargs.get('class')}" />
          </span>
          <a href="#" class="btn fileupload-exists" data-dismiss="fileupload">
            Remove image</a>
        </div>
      </div>
      % if should_clear_above_help:
        <div class="clear">
        </div>
      % endif
      <div class="help help-${help_position}">
        % if help:
          ${help}
        % endif
        <div class="field-error">
          % if renderer.errors_for(name):
            % for error_message in renderer.errors_for(name):
              ${error_message}.
            % endfor
          % endif
        </div>
      </div>
    </div>
  </div>
</%def>