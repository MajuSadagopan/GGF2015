// =================== CONSTANTS ==========================================

PAGE_WIDTH = window.innerWidth;
PAGE_HEIGHT = window.innerHeight;

FORWRD_ACC = 3;
SIDEWAYS_ACC = 3;
ROTATION_ACC = 5;
LOCATION_BUFFER = 80;
ANGLE_BUFFER = 5
CLICK_ROTATION = 5

//============================== Images and dimensions ======================================

MOUSE = "pics/mouse_med.png"
MOUSE_WIDTH = 153
MOUSE_HEIGHT = 243


// ============================== Helper functions ==========================================

function sideLen(xFirst, yFirst, xSecond, ySecond){
	side = Math.sqrt(Math.pow((xFirst-xSecond), 2) + Math.pow((yFirst-ySecond), 2));
	return side;
}

function angle(a,b,c){
	f = (Math.pow(a,2) + Math.pow(b,2) - Math.pow(c,2))/(2*a*b);
	y = Math.acos(f);
	return y;
}

function to_radians(angle){
	radians = angle*0.0174532925;
	return radians;
}

function to_degrees(angle){
	degrees = angle*57.2957795;
	return degrees;
}

// ================== The base_class object ======================================================

function base_class(div, xPos, yPos, image, image_width, image_height){
	// core variables
	this.div = div;
	this.xPos= xPos;
	this.yPos= yPos;
	this.image = image;
	this.width= image_width;
	this.height= image_height;
	
	this.centerX = xPos + (this.width/2);
	this.centerY = yPos + (this.height/2);
	this.noseX = 0;
	this.noseY = 0;
	this.xVelocity = 0;
	this.yVelocity = 0;
	this.forwardACC = 0;
	this.SIDEWAYS_ACC = 0;
	this.friction = 0.10;
	this.angle = 0;
	this.radians = this.angle*0.0174532925
	this.rotation = 0;
	this.sin = 0;
	this.cos = 0;
	this.targetX = 0;
	this.targetY = 0;
	this.target_angle = 0;
	this.clickControl = false;
}

//============ PROTOTYPE FUNCTIONS (Common object functions) ================================	
//============ Initializes object image and dimensions ======================================
base_class.prototype.initiate = function(){
	
	name_id = this.div.substring(1,this.div.length)
	
	$('body').append("<div id="+name_id+"></div>");
	
	$(this.div).css({
			'position':'absolute',
			'z-index':1,
			'background':'url('+this.image+') no-repeat',
			'width':this.width,
			'height':this.height,
		});
		
}

//============ Calculates centre position and nose position of object =====================	
base_class.prototype.center = function(){
		this.centerX = this.xPos + (this.width/2);
		this.centerY = this.yPos +(this.height/2);
		this.noseX = this.centerX +(this.height/2)*this.sin;
		this.noseY = this.centerY -(this.height/2)*this.cos;
};

// ================ Keeps object within boundary
base_class.prototype.boundary = function(){
		if(this.xPos > PAGE_WIDTH){
			this.xPos = 0;
		}
		if(this.xPos< -50){
			this.xPos = PAGE_WIDTH;
		}
		if(this.yPos > PAGE_HEIGHT+150){
			this.yPos = 0;
		}
		if(this.yPos< -150){
			this.yPos = PAGE_HEIGHT;
		}
}


base_class.prototype.clickMove = function(){
		// Converts negative angles into positive angles
		if(this.angle<0){
			this.angle = 360 + this.angle
		}
	
		// If the object nose is within buffer distance of target acc is stopped, if angle is within angle buffer, rotation is stoppped
		if(((this.targetX+LOCATION_BUFFER) > this.noseX) && ((this.targetX-LOCATION_BUFFER) < this.noseX) && ((this.targetY+LOCATION_BUFFER) > this.noseY) && ((this.targetY-LOCATION_BUFFER) < this.noseY)){
			this.clickControl = false;
			this.rotation = 0
			this.forwardACC = 0;
			
		}
		else{
			if(this.angle > this.target_angle - ANGLE_BUFFER && this.angle < this.target_angle + ANGLE_BUFFER){
				this.forwardACC = FORWRD_ACC -1
				this.rotation = 0
			}
		}
}

// ================= MOVE FUNCTION ========================================================	
base_class.prototype.move = function(){
		
		this.center();
		this.boundary();
		
		if(this.clickControl == true){
			this.clickMove();
		};
		
		
// ==== used to update rotation ===============================================
		this.angle += this.rotation
		if(this.angle>360){
			this.angle -= 360;
		}
		else if(this.angle<-360){
			this.angle += 360;
		}
		$(this.div).css({
			'-webkit-transform':'rotate('+this.angle+'deg)',
			'-moz-transform':'rotate('+this.angle+'deg)',
			'-o-transform':'rotate('+this.angle+'deg)',
			'transform':'rotate('+this.angle+'deg)',
		});
		this.radians = this.angle*0.0174532925;
		$('#stats').html(this.centerX+"<br>"+this.centerY+"<br>"+this.angle);

// ====>>>>>>>> used to update direction <<<<<<<<<=============================================		
		
		this.sin = Math.sin(this.radians);
		this.cos = Math.cos(this.radians);
		sinSide = Math.sin(this.radians + 1.5707);
		cosSide = Math.cos(this.radians + 1.5707);
		
// ==== used to update y position ===============================================
		this.yVelocity += ((this.forwardACC*this.cos) + (this.SIDEWAYS_ACC*cosSide) - (this.friction*this.yVelocity));
		this.yPos += (-1*this.yVelocity);
		$(this.div).css('top', this.yPos);
		
		
// ==== used to update x position ===============================================	
		this.xVelocity += ((this.forwardACC*this.sin) + (this.SIDEWAYS_ACC*sinSide) - this.friction*this.xVelocity);
		this.xPos += this.xVelocity;
		$(this.div).css('left', this.xPos);

//===== position checks ========================================================
		$('#check1').css({'top':this.centerY, 'left':this.centerX})
		$('#check2').css({'top': this.noseY, 'left': this.noseX})
			
};

//============ Rotates object in target(X,Y) direction =====================		
base_class.prototype.rotate_to_object = function(x,y){
		this.forwardACC = 0;
		this.targetX = x;
		this.targetY = y;
		this.clickControl = true;
		
		// this.angle = 90;
		
		this.centerX 
		this.centerY
		adjacent_side = y-this.centerY
		hypotenuse = sideLen(this.centerX, this.centerY,x,y)
		angle_radian = Math.acos(adjacent_side/hypotenuse)
		angle_degrees = to_degrees(angle_radian)
		
	//=============== Angle adjustments for grid orientation ============================
		if(x>this.centerX){
			this.target_angle = 180 - angle_degrees
		}
		else{
			this.target_angle = 180 + angle_degrees
		}
	//=============== Angle adjustments for grid orientation ============================		
		angle_diff = Math.abs(this.target_angle-this.angle)
		angle_opposite = Math.abs((360 - this.target_angle) + this.angle)
		
		if(this.target_angle>this.angle){
			if (angle_diff > 180){
				this.rotation = -CLICK_ROTATION
			}
			else{
				this.rotation = CLICK_ROTATION
			}
		}
		else{
			if (angle_diff > 180){
				this.rotation = CLICK_ROTATION
			}
			else{
				this.rotation = -CLICK_ROTATION
			}
		}
		
};

//============ END OF BASE CLASS PROTOTYPES FUNCTIONS (Common object functions for base_class) ===========



//============ SHIP class extension of base-class ===========
function ship(div, xPos, yPos, image, image_width, image_height){
	// core variables
	this.div = div;
	this.xPos= xPos;
	this.yPos= yPos;
	this.image = image;
	this.width= image_width;
	this.height= image_height;
};

ship.prototype = new base_class();

//============ KeyDowns and KeyUps =========================================
ship.prototype.keyDown = function(event){
		this.clickControl = false;
		
		if (event.which == 38){
			this.forwardACC = FORWRD_ACC;
			// $(this.div).css("background", "url('../pics/submarineMotion.png') no-repeat");
		}
		if (event.which == 40){
			this.forwardACC = -1*FORWRD_ACC;
		}
		if (event.which == 65){
			this.SIDEWAYS_ACC = -1*SIDEWAYS_ACC;
		}
		if (event.which == 68){
			this.SIDEWAYS_ACC = FORWRD_ACC;
		}
		if (event.which == 37){
			this.rotation = -1*ROTATION_ACC;
		}
		if (event.which == 39){
			this.rotation = ROTATION_ACC;
		}
};
	
ship.prototype.keyUp = function(){
		// $(this.div).css("background", "url('../pics/submarineMotion.png') no-repeat");
		this.forwardACC = 0;
		this.SIDEWAYS_ACC = 0;
		this.rotation = 0;
};


// ============ MOUSE class extension of base class =========================
function mouse(div, xPos, yPos, image, image_width, image_height){
	// core variables
	this.div = div;
	this.xPos= xPos;
	this.yPos= yPos;
	this.image = image;
	this.width= image_width;
	this.height= image_height;
}; 

mouse.prototype = new base_class();

mouse.prototype.follow = function(){
	if(((this.targetX+LOCATION_BUFFER) > this.noseX) && ((this.targetX-LOCATION_BUFFER) < this.noseX) && ((this.targetY+LOCATION_BUFFER) > this.noseY) && ((this.targetY-LOCATION_BUFFER) < this.noseY)){
			this.clickControl = false;
			
	}
	else{
		this.clickControl = true;
	}
}


$(document).ready(function(){
	
	Zhip = new ship('#kship',PAGE_WIDTH/2, PAGE_HEIGHT/2,MOUSE, MOUSE_WIDTH, MOUSE_HEIGHT);
	Zhip.initiate();
	
	mice = new mouse('#meece',PAGE_WIDTH/3, PAGE_HEIGHT/3,MOUSE, MOUSE_WIDTH, MOUSE_HEIGHT);
	mice.initiate();
	
	$('#stats').html(Zhip.angle);
	$('#game').css({'height':PAGE_HEIGHT, 'width':PAGE_WIDTH,});
	
	
    $(document).click(function(event){
		Zhip.rotate_to_object(event.pageX,event.pageY);
		$("span").text(event.pageX + ", " + event.pageY +", Target Angle: "+Zhip.target_angle);
	});
	

	$(document).keydown(function(event){
		Zhip.keyDown(event);
	});
	
	$(document).keyup(function(event){
		Zhip.keyUp();
	});
	
	function myTimer() {
		Zhip.move();
		mice.move();
		mice.rotate_to_object(Zhip.xPos,Zhip.yPos);
	}
	
	var myVar=setInterval(function(){myTimer()},10);
});