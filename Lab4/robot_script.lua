sim = require('sim')

-- Pioneer P3DX: їзда по лінії, об'їзд перешкод (алгоритм Брайтенберга)
-- з поверненням на лінію та слід руху.
-- Стани: 'line' - їде по лінії, 'avoid' - об'їжджає перешкоду,
--        'pass' - їде паралельно лінії повз перешкоду, 'return' - повертається на лінію.

function sysCall_init()
    robot = sim.getObject('..')
    motorLeft = sim.getObject('../leftMotor')
    motorRight = sim.getObject('../rightMotor')

    -- ультразвукові датчики бачать усе, крім самого робота
    local obstacles = sim.createCollection(0)
    sim.addItemToCollection(obstacles, sim.handle_all, -1, 0)
    sim.addItemToCollection(obstacles, sim.handle_tree, robot, 1)
    usensors = {}
    for i = 1, 16 do
        usensors[i] = sim.getObject('../ultrasonicSensor', {index = i - 1})
        sim.setObjectInt32Param(usensors[i], sim.proxintparam_entity_to_detect, obstacles)
    end
    noDetectionDist = 0.5
    maxDetectionDist = 0.2
    detect = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
    braitenbergL = {-0.2, -0.4, -0.6, -0.8, -1, -1.2, -1.4, -1.6, 0, 0, 0, 0, 0, 0, 0, 0}
    braitenbergR = {-1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0, 0, 0, 0, 0, 0, 0, 0}

    -- датчики лінії під передньою частиною корпусу
    floorSensors = {
        sim.getObject('../leftLineSensor'),
        sim.getObject('../middleLineSensor'),
        sim.getObject('../rightLineSensor')
    }

    v0 = 2              -- швидкість обертання коліс, рад/с (~0,2 м/с)
    turnK = 0.25        -- частка швидкості внутрішнього колеса на повороті
    passTime = 1.5      -- скільки секунд їхати паралельно лінії після об'їзду
    returnAngle = math.rad(55) -- під яким кутом повертатися на лінію

    state = 'line'
    lastSide = 0        -- з якого боку лінію бачили востаннє: -1 ліворуч, 1 праворуч
    lineYaw = 0         -- напрямок лінії перед перешкодою
    turnSum = 0         -- куди сумарно відвертав робот під час об'їзду (>0 - праворуч)
    stateTime = 0

    -- слід руху: жовта ламана з останніх 2000 точок
    robotTrace = sim.addDrawingObject(sim.drawing_linestrip + sim.drawing_cyclic, 2, 0, -1, 2000, {1, 1, 0})
end

function sysCall_sensing()
    sim.addDrawingObjectItem(robotTrace, sim.getObjectPosition(robot))
end

function readLine()
    local onLine = {false, false, false}
    for i = 1, 3 do
        local result, data = sim.readVisionSensor(floorSensors[i])
        if result >= 0 then
            onLine[i] = data[11] < 0.5 -- data[11]: середня яскравість зображення датчика
        end
    end
    return onLine
end

function yaw()
    return sim.getObjectOrientation(robot)[3]
end

function angleDiff(a, b)
    local d = a - b
    return math.atan(math.sin(d), math.cos(d))
end

function setState(s)
    state = s
    stateTime = sim.getSimulationTime()
end

-- рух у заданому напрямку: різниця швидкостей коліс пропорційна похибці курсу
function headTo(target)
    local err = angleDiff(target, yaw())
    local k = math.max(-1.5, math.min(1.5, 3 * err))
    return v0 - k, v0 + k
end

function sysCall_actuation()
    -- перешкоди
    local obstacle = false
    for i = 1, 16 do
        local res, dist = sim.readProximitySensor(usensors[i])
        if res > 0 and dist < noDetectionDist then
            if dist < maxDetectionDist then dist = maxDetectionDist end
            detect[i] = 1 - (dist - maxDetectionDist) / (noDetectionDist - maxDetectionDist)
            obstacle = true
        else
            detect[i] = 0
        end
    end

    local line = readLine()
    local seeLine = line[1] or line[2] or line[3]
    local t = sim.getSimulationTime()
    local vLeft, vRight = v0, v0

    if obstacle then
        if state == 'line' then
            lineYaw = yaw()   -- запам'ятовуємо напрямок лінії
            turnSum = 0
        end
        if state ~= 'avoid' then setState('avoid') end
        -- об'їзд за Брайтенбергом: чим ближче перешкода, тим сильніше відвертаємо
        for i = 1, 16 do
            vLeft = vLeft + braitenbergL[i] * detect[i]
            vRight = vRight + braitenbergR[i] * detect[i]
        end
        turnSum = turnSum + (vLeft - vRight)
    elseif state == 'avoid' then
        setState('pass')
        vLeft, vRight = headTo(lineYaw)
    elseif state == 'pass' then
        -- їдемо паралельно лінії, щоб проминути перешкоду
        vLeft, vRight = headTo(lineYaw)
        if t - stateTime > passTime then setState('return') end
    elseif state == 'return' then
        if seeLine then
            setState('line')
        else
            -- відвертав праворуч - повертаємося ліворуч, і навпаки
            local side = (turnSum > 0) and 1 or -1
            vLeft, vRight = headTo(lineYaw + side * returnAngle)
        end
    end

    if state == 'line' then
        if seeLine then
            if line[1] and not line[3] then
                vLeft = turnK * v0      -- лінія ліворуч: повертаємо ліворуч
                lastSide = -1
            elseif line[3] and not line[1] then
                vRight = turnK * v0     -- лінія праворуч: повертаємо праворуч
                lastSide = 1
            end
        elseif lastSide < 0 then
            vLeft = -0.2 * v0           -- лінію втрачено: розвертаємося туди, де бачили її востаннє
        elseif lastSide > 0 then
            vRight = -0.2 * v0
        end
    end

    sim.setJointTargetVelocity(motorLeft, vLeft)
    sim.setJointTargetVelocity(motorRight, vRight)
end
