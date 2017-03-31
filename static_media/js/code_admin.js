(function($){

	$(document).ready(function(){

	var valor_dueno = $('#id_dueno').val();
	if (valor_dueno === '1'){
		$('#duenosi_set-group').show();
		$('#duenono_set-group').hide();
	}
	else if (valor_dueno === '2'){
		$('#duenosi_set-group').hide();
		$('#duenono_set-group').show();
	}
	else{
		$('#duenosi_set-group').hide();
		$('#duenono_set-group').hide();
	}

	var valor_panelsolar = $('#id_tipoenergia_set-0-tipo_2').val();
	if (valor_panelsolar === '4') {
		$('#panelsolar_set-group').show();
	}else{
		$('#panelsolar_set-group').hide();
	};

	var valor_contaminada = $('#id_calidadagua_set-0-calidad').val();
	if (valor_contaminada === '3') {
		$('#contaminada_set-group').show();
		$('#evidencia_set-group').show();
	}else{
		$('#contaminada_set-group').hide();
		$('#evidencia_set-group').hide();
	};

	var valor_otro_ingreso = $('#id_percibeingreso_set-0-si_no').val();
	if (valor_otro_ingreso === '1') {
		$('#fuentes_set-group').show();
	}else{
		$('#fuentes_set-group').hide();
	};

	var valor_41 = $('#id_seguridadalimentaria_set-0-consumo_diario').val();
	if (valor_41 === '2') {
		$('#respuestano41_set-group').show();
	}else{
		$('#respuestano41_set-group').hide();
	};

	$('#id_dueno').change(function(){
			var valor_tipo = $('#id_dueno').val();
			if (valor_tipo === '1' ) {
				$('#duenosi_set-group').show();
				$('#duenono_set-group').hide();
			}else{
				$('#duenosi_set-group').hide();
				$('#duenono_set-group').show();
			};
	});

	$('#id_calidadagua_set-0-calidad').change(function(){
			var valor_tipo = $('#id_calidadagua_set-0-calidad').val();
			if (valor_tipo === '3' ) {
				$('#contaminada_set-group').show();
				$('#evidencia_set-group').show();
			}else{
				$('#contaminada_set-group').hide();
				$('#evidencia_set-group').hide();
			};
	});

	$('#id_percibeingreso_set-0-si_no').change(function(){
			var valor_tipo = $('#id_percibeingreso_set-0-si_no').val();
			if (valor_tipo === '1' ) {
				$('#fuentes_set-group').show();
			}else{
				$('#fuentes_set-group').hide();
			};
		});

	$('#id_seguridadalimentaria_set-0-consumo_diario').change(function(){
			var valor_tipo = $('#id_seguridadalimentaria_set-0-consumo_diario').val();
			if (valor_tipo === '2' ) {
				$('#respuestano41_set-group').show();
			}else{
				$('#respuestano41_set-group').hide();
			};
		});

	});
})(jQuery || django.jQuery)
