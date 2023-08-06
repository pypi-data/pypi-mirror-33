## -*- coding: utf-8; -*-

<%def name="keypad(unit_uom, selected_uom, quantity=1, allow_cases=True)">
  <div class="quantity-keypad-thingy" data-changed="false">

    <table>
      <tbody>
        <tr>
          <td>${h.link_to("7", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("8", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("9", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
        </tr>
        <tr>
          <td>${h.link_to("4", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("5", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("6", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
        </tr>
        <tr>
          <td>${h.link_to("1", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("2", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("3", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
        </tr>
        <tr>
          <td>${h.link_to("0", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to(".", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
          <td>${h.link_to("Del", '#', class_='keypad-button ui-btn ui-btn-inline ui-corner-all')}</td>
        </tr>
      </tbody>
    </table>

    <fieldset data-role="controlgroup" data-type="horizontal">
      <button type="button" class="ui-btn-active keypad-quantity">${h.pretty_quantity(1 if quantity is None else quantity)}</button>
      <button type="button" disabled="disabled">&nbsp;</button>
      % if allow_cases:
      ${h.radio('keypad-uom', value='CS', checked=selected_uom == 'CS', label="CS")}
      % endif
      ${h.radio('keypad-uom', value=unit_uom, checked=selected_uom == unit_uom, label=unit_uom)}
    </fieldset>

  </div>
</%def>
