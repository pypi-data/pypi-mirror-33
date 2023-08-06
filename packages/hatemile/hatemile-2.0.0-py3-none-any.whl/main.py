from hatemile.util.configure import Configure
from hatemile.util.html.bs.bshtmldomparser import BeautifulSoupHTMLDOMParser
from hatemile.util.css.tinycss.tinycssparser import TinyCSSParser
from hatemile.implementation.display import AccessibleDisplayImplementation
from hatemile.implementation.css import AccessibleCSSImplementation
from hatemile.implementation.event import AccessibleEventImplementation
from hatemile.implementation.form import AccessibleFormImplementation
from hatemile.implementation.navig import AccessibleNavigationImplementation
from hatemile.implementation.assoc import AccessibleAssociationImplementation

configure = Configure()
htmlCode = """<!DOCTYPE html>
	<html lang="pt-br">
		<head>
			<title>HaTeMiLe Tests</title>
			<meta charset="UTF-8" />
			<style type="text/css">
			    table {
			        speak-header: always;
			    }
			</style>
		</head>
		<body>
			<h1>HaTeMiLe Tests ..</h1>
			<!-- Events -->
			<div>
				<h2>Test Events</h2>
				<a href="#" onclick="alert('Alert A')">Alert</a>
				<button onclick="alert('Alert Button')">Alert</button>
				<input type="button" onclick="alert('Alert Input')" value="Alert" />
				<span onclick="alert('Alert Span')" style="background: red;">Alert</span>
				<i onclick="alert('Alert I')">Alert</i>
				<div style="height: 300px; width: 300px; border: 1px solid black" onclick="alert('Alert Div')">
					Alert
				</div>
				<span onclick="alert('Alert span')" onkeypress="console.log('Console SPAN')" style="background: blueviolet;">Console</span>
				<hr />
				<a href="#" onmouseover="console.log('Over A')" onmouseout="console.log('Out A')">Console</a>
				<button onmouseover="console.log('Over Button')" onmouseout="console.log('Out Button')">Console</button>
				<input type="button" onmouseover="console.log('Over Input')" value="Console" onmouseout="console.log('Out Input')" />
				<span onmouseover="console.log('Over Span')" style="background: red;" onmouseout="console.log('Out Span')">Console</span>
				<i onmouseover="console.log('Over I')" onmouseout="console.log('Out I')">Console</i>
				<div style="height: 300px; width: 300px; border: 1px solid black" ondrop="event.preventDefault();event.target.appendChild(document.getElementById(event.dataTransfer.getData('text')));" ondragover="event.preventDefault();">
					Console
				</div>
				<span id="draggable-item" ondragstart="event.dataTransfer.setData('text', event.target.id);" draggable="true">Drag-and-Drop</span>
			</div>
			<!-- Forms -->
			<form autocomplete="off" id="form1">
				<h2>Test Forms</h2>
				<label for="field1">Field1</label>
				<input type="text" value="" required="required" id="field1" autocomplete="on" />
				<label>
					Field2
					<div>
						<input type="text" value="" required="required" autocomplete="off" />
					</div>
				</label>
				<label for="field3">Field3</label>
				<textarea required="required" id="field3" autocomplete></textarea>
				<label>
					Field4
					<textarea required="required" autocomplete="none"></textarea>
				</label>
				<label for="field5">Field5</label>
				<select required="required" id="field5">
					<option value="">0</option>
					<option value="1">1</option>
					<option value="2">2</option>
				</select>
				<label>
					Field6
					<select required="required">
						<option value="">0</option>
						<option value="1">1</option>
						<option value="2">2</option>
					</select>
				</label>
				<label for="field7">Field7</label>
				<input type="number" min="0" value="0" max="10" id="field7" role="spinbu" />
				<input type="submit" value="Submit" />
			</form>
			<input type="text" value="" required="" form="form1" />
			<!-- Images -->
			<div>
				<h2>Test Images</h2>
				<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Handicapped_Accessible_sign.svg/2000px-Handicapped_Accessible_sign.svg.png" alt="Acessibility" longdesc="https://www.wikimedia.org/" />
				<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/HTML5_logo_and_wordmark.svg/2000px-HTML5_logo_and_wordmark.svg.png" alt="HTML5" longdesc="http://www.w3.org/html/" />
			</div>
			<!-- Shortcuts -->
			<form action="http://www.webplatform.org/">
				<h2>Test Shortcuts</h2>
				<a href="http://www.w3.org/html/" title="Go to HTML5" accesskey="q">HTML5</a><br />
				<a href="https://www.wikimedia.org/" accesskey="w">Go to Wikimidia</a><br />
				<label id="label1">Field1</label>
				<input type="text" value="" aria-labelledby="label1" accesskey="e" /><br />
				<input type="text" value="" aria-label="Field 2" accesskey="r" /><br />
				<input type="image" src="https://octodex.github.com/images/octobiwan.jpg" alt="Octobiwan" accesskey="t" /><br />
				<input type="reset" value="Reset button" accesskey="y" /><br />
				<input type="button" value="Show shortcuts" accesskey="u" onclick="alert('Only in client-side version.');" /><br />
				<input type="submit" value="Subit Button" accesskey="i" /><br />
			</form>
			<!-- Tables -->
			<div>
				<h2>Test Tables</h2>
				<table>
					<thead>
						<tr>
							<th rowspan="3">1</th>
							<th rowspan="2">2</th>
							<th>3</th>
							<td>4</td>
						</tr>
						<tr>
							<th colspan="2">1</th>
						</tr>
						<tr>
							<th>1</th>
							<th>2</th>
							<td>3</td>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td></td>
							<td></td>
							<td></td>
							<td></td>
						</tr>
						<tr>
							<td rowspan="2"></td>
							<td></td>
							<th></th>
							<td></td>
						</tr>
						<tr>
							<td colspan="2"></td>
							<td></td>
						</tr>
						<tr>
							<td></td>
							<td></td>
							<td></td>
						</tr>
					</tbody>
				</table>
				<table>
					<tr>
						<th>1</th>
						<td>2</td>
						<th colspan="2">3</th>
					</tr>
					<tr>
						<td>1</td>
						<td colspan="2">2</td>
						<td>3</td>
					</tr>
					<tr>
						<td>1</td>
						<th>2</th>
						<td>3</td>
						<td>4</td>
					</tr>
				</table>
			</div>
		</body>
	</html>"""
parser = BeautifulSoupHTMLDOMParser(htmlCode)
css_parser = TinyCSSParser(parser, 'http://localhost/casa/')

event = AccessibleEventImplementation(parser)
css = AccessibleCSSImplementation(parser, css_parser, configure)
form = AccessibleFormImplementation(parser)
navigation = AccessibleNavigationImplementation(parser, configure)
association = AccessibleAssociationImplementation(parser)
display = AccessibleDisplayImplementation(parser, configure)

event.make_accessible_all_drag_and_drop_events()
event.make_accessible_all_click_events()
event.make_accessible_all_hover_events()

form.mark_all_required_fields()
form.mark_all_range_fields()
form.mark_all_autocomplete_fields()
form.mark_all_invalid_fields()

navigation.provide_navigation_by_all_headings()
navigation.provide_navigation_by_all_skippers()
navigation.provide_navigation_to_all_long_descriptions()

association.associate_all_data_cells_with_header_cells()
association.associate_all_labels_with_fields()

css.provide_all_speak_properties()

display.display_all_shortcuts()
display.display_all_roles()
display.display_all_cell_headers()
display.display_all_waiaria_states()
display.display_all_links_attributes()
display.display_all_titles()
display.display_all_languages()
display.display_all_alternative_text_images()

navigation.provide_navigation_by_all_skippers()
display.display_all_shortcuts()

print(parser.get_html())

print(parser.get_html())
