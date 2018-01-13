
var autoComplete = (function(){
    function autoComplete(input){
        
        // Initialize some attribute
        input.cache = {};
        input.last_term = '';
        
        // Get choices from datalist
        input.datalist = document.getElementById(input.getAttribute('list'));
        input.choices = [];
        for (var i=0; i<input.datalist.options.length; i++){
            input.choices.push(input.datalist.options[i].value)
        };
        
        // Remove reference to datalist and turn off autocomplete
        input.datalist_id = input.getAttribute('list');
        input.setAttribute('list', '')
        
        input.setAttribute('autocomplete', 'off')

        // Insert html for list of suggestions
        input.wrapper = document.createElement('div');
        input.wrapper.classList.add('autocomplete-wrapper');

        input.suggestions = document.createElement('ul');
        input.suggestions.classList.add('autocomplete-suggestions');

        input.wrapper.appendChild(input.suggestions);

        input.parentNode.insertBefore(input.wrapper, input.nextSibling);

        // Methods
        input.prettify = function(haystack, needle){
            needle = needle.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            var re = new RegExp("(" + needle.split(' ').join('|') + ")", "gi");
            return haystack.replace(re, "<b>$1</b>");
        };

        input.renderSuggestions = function(term, suggestions){
            while (input.suggestions.firstChild) {
                input.suggestions.removeChild(input.suggestions.firstChild)
            };
            if ( !suggestions.length ){ 
                input.suggestions.style.display = 'none';
                return;
            };
            for (var i=0; i<suggestions.length; i++){
                var item = document.createElement('li');
                item.setAttribute('value', suggestions[i]);
                item.innerHTML = input.prettify(suggestions[i], term);
                input.suggestions.appendChild(item);
            }
            input.suggestions.style.display = 'block';
        };

        input.makeSuggestions = function(term){
            if (term in input.cache){
                return input.cache[term];
            };
            var matches = [];
            for (var i=0; i<input.choices.length; i++){
                if (input.choices[i].toLowerCase().indexOf(term) != -1){
                    matches.push(input.choices[i])
                }
            };
            input.cache[term] = matches;
            return matches;
        }

        // Event handlers
        input.suggestions.clickHandler = function(event){
            var target = event.target
            input.value = target.getAttribute('value')
        }
        input.suggestions.addEventListener('mousedown', input.suggestions.clickHandler)

        input.keyDownHandler = function(event){
            var key = event.which || event.keyCode;
            // up and down
            if ((key == 38 || key == 40) && input.suggestions.firstChild){
                input.suggestions.style.display = 'block';
                
                var selected = input.suggestions.querySelector('.selected');
                if (!selected){
                    var next = input.suggestions.firstChild;
                }
                else {
                    var next = key == 38 ? selected.previousSibling : selected.nextSibling;
                }

                if (next){
                    if (selected) { selected.classList.remove('selected') };
                    next.classList.add('selected');
                    input.value = next.getAttribute('value');
                }
            };

        };
        input.addEventListener('keydown', input.keyDownHandler);

        input.keyUpHandler = function(event){
            var key = event.which || event.keyCode;
            // tab, arrows
            if (key == 9 || (key >= 37 && key <= 40)){ return };
            // esc
            if (key == 27){
                input.suggestions.style.display = 'none';
                var selected = input.suggestions.querySelector('.selected');
                if (selected){
                    selected.classList.remove('selected');
                };
                input.value = input.last_term;
                return
            };
            var term = input.value.toLowerCase();
            input.last_term = term;
            // empty search term
            if (!term){ return };

            clearTimeout(input.timer);
            input.timer = setTimeout(function(){ input.renderSuggestions(term, input.makeSuggestions(term)) }, 300);
        };
        input.addEventListener('keyup', input.keyUpHandler);

        input.addEventListener('blur', function(event){
            input.suggestions.style.display = 'none';
        });
    };
    return autoComplete
})()

var inputs = document.querySelectorAll('.autocomplete')

for (var i=0; i<inputs.length; i++){
    new autoComplete(inputs[i])
}
