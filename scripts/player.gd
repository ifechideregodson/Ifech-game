extends CharacterBody3D

@export var is_vehicle := false
@export var walk_speed := 7.0
@export var vehicle_speed := 13.0
@export var jump_velocity := 5.0
var touch := {"forward": false, "back": false, "left": false, "right": false}
var jump_requested := false
var gravity := 18.0

func set_touch(direction: String, pressed: bool):
    touch[direction] = pressed

func request_jump():
    jump_requested = true

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= gravity * delta
    else:
        if jump_requested and not is_vehicle:
            velocity.y = jump_velocity
    jump_requested = false

    var forward = Input.get_action_strength("move_forward") - Input.get_action_strength("move_back")
    var sideways = Input.get_action_strength("move_right") - Input.get_action_strength("move_left")
    if touch.forward: forward += 1
    if touch.back: forward -= 1
    if touch.right: sideways += 1
    if touch.left: sideways -= 1
    var input_dir = Vector2(sideways, forward).normalized()
    var speed = vehicle_speed if is_vehicle else walk_speed
    var direction = Vector3(input_dir.x, 0, -input_dir.y).rotated(Vector3.UP, rotation.y)
    if direction.length() > 0.05:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
        rotation.y = lerp_angle(rotation.y, atan2(-direction.x, -direction.z), delta * 8.0)
    else:
        velocity.x = move_toward(velocity.x, 0, speed * 5 * delta)
        velocity.z = move_toward(velocity.z, 0, speed * 5 * delta)
    if is_vehicle:
        velocity.y = 0
    move_and_slide()
