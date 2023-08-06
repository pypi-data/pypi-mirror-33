function loadNetFiles() {
	function getJsonFromUrl(hashBased) {
		var query;
		if(hashBased) {
			var pos = location.href.indexOf("?");
			if(pos==-1) return [];
			query = location.href.substr(pos+1);
		} else {
			query = location.search.substr(1);
		}
		var result = {};
		query.split("&").forEach(function(part) {
			if(!part) return;
			part = part.split("+").join(" "); // replace every + with space, regexp-free version
			var eq = part.indexOf("=");
			var key = eq>-1 ? part.substr(0,eq) : part;
			var val = eq>-1 ? decodeURIComponent(part.substr(eq+1)) : "";
			var from = key.indexOf("[");
			if(from==-1) result[decodeURIComponent(key)] = val;
			else {
				var to = key.indexOf("]",from);
				var index = decodeURIComponent(key.substring(from+1,to));
				key = decodeURIComponent(key.substring(0,from));
				if(!result[key]) result[key] = [];
				if(!index) result[key].push(val);
				else result[key][index] = val;
			}
		});
		return result;
	}
	var params = getJsonFromUrl();
	var tree = null, metadata = null;
	for (var key in params) {
		params[key] = params[key].replace('www.dropbox.com', 'dl.dropboxusercontent.com');
		if (key === 'tree') {
			tree = params[key];
		} else if (key == 'metadata') {
			metadata = params[key];
		}
	}
	if (tree) {
		$.ajax({
			type: "GET",
			url: tree,
			success: function(tree){
				try {
					data = JSON.parse(tree);
				}
				catch(error) {
					data = {};
					if (tree.substring(0,6)==="#NEXUS"){
						data['nexus']=tree;
					}
					else{
						data['nwk']=tree;
					}
				data['layout_algorithm']=$("#layout-select").val();
				}
				finally {
					tree_raw = data;
					loadMSTree(tree_raw);
				}
				if (the_tree && metadata) {
					$.ajax({
						type: "GET",
						url: metadata,
						success: function(data){
							try {
								var return_data = [];
								var lines = data.split(/\r\n|\r|\n/g);
								var delimiter = lines[0].search(/\t/) >= 0 ? '\t': ',';
								var header = lines[0].split(delimiter);
								var header_index= [];
								for (var i=0;i<header.length;i++){
									header_index[i]=header[i];
								}

								for (var i=1;i<lines.length;i++){
									var map = {};
										var arr = lines[i].split(delimiter);
										for (var col in arr){
											map[header_index[col]]=arr[col];
										}
										return_data.push(map);
								}
								parseMetadata("OK",return_data,header_index);
							}
							catch(error) {
								parseMetadata("Error",error.message)
							}
						}
					});
				}
			}
		});
	}
}


	function filesDropped(files){
		current_metadata_file = null;
		for (var id=0; id < files.length; id += 1) {
			var file = files[id];
			var reader = new FileReader();
			reader.onload = function(progressEvent) {
				distributeFile(this.result, this.filename);
			};
			reader.filename = file.name;
			reader.readAsText(file);
		};
	}
	function distributeFile(text, filename) {
		var head_line = text.substring(0, 2048).split(/[\n\r]/)[0];
		if (head_line.startsWith(">")  || (head_line.startsWith("#") && ! head_line.toUpperCase().startsWith("#NEXUS") )) {
			if (cannot_connect){
				loadFailed("Cannot Connect to the backend server");
				return;
			}
			profile_file=this.file;
			initiateLoading("Reading Profile File");
			$("#param-panel").show();
			$("#modal-ok-button").data("profile_file", text);
			$("#modal-ok-button").html("OK");
			$(waiting_spinner.el).hide();
			$("#modal-title").show().text("Parameters For Tree Creation");
			$("#waiting-information").hide();
			$("#headertag").text(filename);
		}

		else if ((head_line.indexOf(",") >=0 || head_line.indexOf("\t")>=0) && !head_line.startsWith("(") && !head_line.startsWith("[") && !head_line.startsWith(" ") && !head_line.startsWith("{")) {
			var dl = (head_line.indexOf(",") >= 0 ? "," : "\t");
			current_metadata_file = [text, dl];
			if (the_tree) {
				loadMetadataText(text, dl);
			}
		}
		else {
			loadTreeText(text);
			$("#headertag").text(filename);
		}
	}

	function loadMetadataText(text, delimiter){
		var return_data=[];
		try{
			var lines =  text.split(/\r\n|\r|\n/g);
			var header = lines[0].split(delimiter);
			for (var i=1;i<lines.length;i++){
				var map = {};
					var arr = lines[i].split(delimiter);
					for (var col in arr){
						map[header[col]]=arr[col];
					}
					return_data.push(map);
			}
			parseMetadata("OK",return_data,header);
		}catch(error){
			parseMetadata("Error",error.message)
		}
	};

	function parseMetadata (msg,lines,header_index){
		if( msg === 'Error') {
			alert('malformed metadata file');
		}
		var meta={};
		if (header_index.find(function(d) {return d == "ID"})) {
			id_name = 'ID';
		} else {
			id_name = header_index[0];
		}
		for (var i in lines){
			var line = lines[i];
			meta[line[id_name]]=line;
		}

		var category = 'nothing';
		var options={};
		category = header_index.length > 1 ? header_index[1] : header_index[0];
		for (var i in header_index){
			var header = header_index[i];
			options[header]=header;
		}
		the_tree.addMetadataOptions(options);
		$("#metadata-select").val(category);
		the_tree.addMetadata(meta);
		the_tree.changeCategory(category);
};


	function loadTreeText(tree){
		initiateLoading("Processing tree file")
		//give time to dialog to display
		setTimeout(function(){
			try {
				data =JSON.parse(tree);
			} catch (e) {
				data = {};
				if ( tree.toUpperCase().startsWith('#NEXUS') ) {
					data['nexus'] = tree;
					data['layout_algorithm']=$("#layout-select").val();
				}
				else{
					data['nwk']=tree;
					data['layout_algorithm']=$("#layout-select").val();
				}
			}
			tree_raw = data;
			loadMSTree(tree_raw);
		},500);
};

function saveTextAsFile (text,suggested_name){
	var save = $("<a download><button>Save</button></a>").click(function(){
		var name=$("#filename").val();
		if(!name){
			return;
		}
		//windows - don't actually use the file download anchor
		if(window.navigator.msSaveOrOpenBlob) {
			var data = new Blob([text], {type: 'text/plain'});
			window.navigator.msSaveBlob(data,name);
		}
		//others
		else{
			var data = new Blob([text], {type: 'text/plain'});

			this.textFile = window.URL.createObjectURL(data);
			//set file name and contents before click event propogates
			$(this).attr("download",name);
			$(this).attr("href",this.textFile);

		}
		$(this).parent().dialog().dialog("close");
	});

	var notification = "<p style='font-size:10'> Some browsers allow you to select a folder after you click the 'Save' Button.<br> Whereas many browsers, such as Chrome, by default save the downloaded file into:<br><b>Windows</b>: <code>'&#92;Users&#92;&lt;username&gt;&#92;Downloads'</code><br><b>Mac</b>: <code>'/Users/&lt;username&gt;/Downloads'</code><br><b>Linux</b>: <code>'home/&lt;username&gt;/Downloads'</code><br></p>";
	var filenamebar = $("<input title='Suffix will be automatically added in some browsers if you have got a file with the same name.' type='text' id ='filename' value='"+suggested_name+"'>");
	//the actual dailog box
	$("<div id ='savedailog'></div>")
	.html(notification + "File Name: ")
	.dialog({
		autoOpen: true,
		modal: true,
		title: "Save File",
		buttons: {
			"Cancel": function () {
				$(this).dialog("close");
			}
		},
		close: function () {
			$(this).dialog('destroy').remove();
		},
		width: "400px",
	}).append(filenamebar).append(save);
};