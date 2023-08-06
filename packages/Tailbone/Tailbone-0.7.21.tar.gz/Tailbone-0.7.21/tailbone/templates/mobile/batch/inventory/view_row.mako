## -*- coding: utf-8; -*-
<%inherit file="/mobile/batch/view_row.mako" />
<%namespace file="/mobile/keypad.mako" import="keypad" />

## TODO: this is broken for actual page (header) title
<%def name="title()">${h.link_to("Inventory", url('mobile.batch.inventory'))} &raquo; ${h.link_to(batch.id_str, url('mobile.batch.inventory.view', uuid=batch.uuid))} &raquo; ${row.upc.pretty()}</%def>

<%
   unit_uom = 'LB' if row.product and row.product.weighed else 'EA'

   if row.cases and allow_cases:
       uom = 'CS'
   elif row.units:
       uom = unit_uom
   elif row.case_quantity and allow_cases:
       uom = 'CS'
   else:
       uom = unit_uom
%>

<div class="ui-grid-a">
  <div class="ui-block-a">
    % if instance.product:
        <h3>${row.brand_name or ""}</h3>
        <h3>${row.description} ${row.size}</h3>
        <h3>${h.pretty_quantity(row.case_quantity)} ${unit_uom} per CS</h3>
    % else:
        <h3>${row.description}</h3>
    % endif
  </div>
  <div class="ui-block-b">
    ${h.image(product_image_url, "product image")}
  </div>
</div>

<p>
  currently:&nbsp; 
  % if uom == 'CS':
      ${h.pretty_quantity(row.cases or 0)}
  % else:
      ${h.pretty_quantity(row.units or 0)}
  % endif
  ${uom}
</p>

% if not batch.executed and not batch.complete:

    ${h.form(request.current_route_url())}
    ${h.csrf_token(request)}
    ${h.hidden('row', value=row.uuid)}
    % if allow_cases:
    ${h.hidden('cases')}
    % endif
    ${h.hidden('units')}

    <%
       quantity = 1
       if allow_cases:
           if row.cases is not None:
               quantity = row.cases
           elif row.units is not None:
               quantity = row.units
       elif row.units is not None:
           quantity = row.units
    %>
    ${keypad(unit_uom, uom, quantity=quantity, allow_cases=allow_cases)}

    <fieldset data-role="controlgroup" data-type="horizontal" class="inventory-actions">
      <button type="button" class="ui-btn-inline ui-corner-all save">Save</button>
      <button type="button" class="ui-btn-inline ui-corner-all delete" disabled="disabled">Delete</button>
      ${h.link_to("Cancel", url('mobile.batch.inventory.view', uuid=batch.uuid), class_='ui-btn ui-btn-inline ui-corner-all')}
    </fieldset>

    ${h.end_form()}

% endif
