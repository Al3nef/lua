local player = game.Players.LocalPlayer
local CoreGui = game:GetService("CoreGui")
local TweenService = game:GetService("TweenService")

-- تنظيف النسخ القديمة
if CoreGui:FindFirstChild("GapsTeleport_SmartV2") then
    CoreGui:FindFirstChild("GapsTeleport_SmartV2"):Destroy()
end

-- 1. بناء الواجهة
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "GapsTeleport_SmartV2"
ScreenGui.Parent = CoreGui
ScreenGui.ResetOnSpawn = false

local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, 240, 0, 240)
MainFrame.Position = UDim2.new(0.5, -120, 0.5, -120)
MainFrame.BackgroundColor3 = Color3.fromRGB(54, 54, 62)
MainFrame.Active = true
MainFrame.Draggable = true
MainFrame.Parent = ScreenGui
Instance.new("UICorner", MainFrame).CornerRadius = UDim.new(0, 15)

-- الهيدر
local Header = Instance.new("Frame")
Header.Size = UDim2.new(1, 0, 0, 40)
Header.BackgroundColor3 = Color3.fromRGB(34, 34, 42)
Header.Parent = MainFrame
Instance.new("UICorner", Header).CornerRadius = UDim.new(0, 15)

local Title = Instance.new("TextLabel")
Title.Text = "⚡ GAPS TELEPORT"
Title.Size = UDim2.new(1, 0, 1, 0)
Title.TextColor3 = Color3.new(1, 1, 1)
Title.Font = Enum.Font.FredokaOne
Title.BackgroundTransparency = 1
Title.Parent = Header

-- نص الحالة (يتحدث تلقائياً عند الفتح)
local RegionLabel = Instance.new("TextLabel")
RegionLabel.Text = "جاري الفحص..." 
RegionLabel.Size = UDim2.new(1, 0, 0, 40)
RegionLabel.Position = UDim2.new(0, 0, 0.18, 0)
RegionLabel.TextColor3 = Color3.new(1, 1, 1)
RegionLabel.Font = Enum.Font.FredokaOne
RegionLabel.TextSize = 18
RegionLabel.BackgroundTransparency = 1
RegionLabel.Parent = MainFrame

-- 2. الإحداثيات (المناطق 1-9)
local zonePositions = {
    [1] = Vector3.new(202.10, -2.77, 11.31),
    [2] = Vector3.new(287.36, -2.77, 14.88),
    [3] = Vector3.new(401.02, -2.77, 9.29),
    [4] = Vector3.new(546.41, -2.77, 8.80),
    [5] = Vector3.new(758.99, -2.77, 2.89),
    [6] = Vector3.new(1074.44, -2.77, 10.90),
    [7] = Vector3.new(1557.52, -2.77, 12.84),
    [8] = Vector3.new(2245.62, -2.77, 14.52),
    [9] = Vector3.new(2625.31, -2.77, 13.72),
}

local currentZone = 0 

-- وظيفة التعرف التلقائي على مكانك (مثل نظام الـ VIP)
local function autoDetectLocation()
    local char = player.Character
    local hrp = char and char:FindFirstChild("HumanoidRootPart")
    if hrp then
        local closest = 0
        local minDistance = 50 -- المدى المسموح للكشف
        
        for i, pos in ipairs(zonePositions) do
            local dist = (hrp.Position - pos).Magnitude
            if dist < minDistance then
                closest = i
                minDistance = dist
            end
        end
        
        currentZone = closest
        if currentZone > 0 then
            RegionLabel.Text = "المنطقة " .. currentZone
        else
            RegionLabel.Text = "انتظار النقل..."
        end
    end
end

-- وظيفة الانتقال السلس والسريع
local function sonicTeleport(targetPos)
    local char = player.Character
    local hrp = char and char:FindFirstChild("HumanoidRootPart")
    if hrp then
        local distance = (hrp.Position - targetPos).Magnitude
        local speed = 1200 
        local duration = distance / speed
        local tweenInfo = TweenInfo.new(duration, Enum.EasingStyle.Linear)
        local tween = TweenService:Create(hrp, tweenInfo, {CFrame = CFrame.new(targetPos + Vector3.new(0, 3, 0))})
        tween:Play()
    end
end

-- 3. برمجة الأزرار
local UpBtn = Instance.new("TextButton")
UpBtn.Text = "⬆️ UP"
UpBtn.Size = UDim2.new(0, 100, 0, 45)
UpBtn.Position = UDim2.new(0.05, 0, 0.38, 0)
UpBtn.BackgroundColor3 = Color3.fromRGB(65, 65, 75)
UpBtn.TextColor3 = Color3.new(1, 1, 1)
UpBtn.Font = Enum.Font.FredokaOne
UpBtn.Parent = MainFrame
Instance.new("UICorner", UpBtn)

UpBtn.MouseButton1Click:Connect(function()
    if currentZone < 9 then
        currentZone = currentZone + 1
        RegionLabel.Text = "المنطقة " .. currentZone
        sonicTeleport(zonePositions[currentZone])
    end
end)

local DownBtn = Instance.new("TextButton")
DownBtn.Text = "⬇️ DOWN"
DownBtn.Size = UDim2.new(0, 100, 0, 45)
DownBtn.Position = UDim2.new(0.53, 0, 0.38, 0)
DownBtn.BackgroundColor3 = Color3.fromRGB(65, 65, 75)
DownBtn.TextColor3 = Color3.new(1, 1, 1)
DownBtn.Font = Enum.Font.FredokaOne
DownBtn.Parent = MainFrame
Instance.new("UICorner", DownBtn)

DownBtn.MouseButton1Click:Connect(function()
    if currentZone > 1 then
        currentZone = currentZone - 1
        RegionLabel.Text = "المنطقة " .. currentZone
        sonicTeleport(zonePositions[currentZone])
    elseif currentZone == 1 then
        currentZone = 0
        RegionLabel.Text = "انتظار النقل..."
    end
end)

-- بقية الأزرار
local ZoomBtn = Instance.new("TextButton")
ZoomBtn.Text = "🔓 UNLOCK ZOOM"
ZoomBtn.Size = UDim2.new(0.9, 0, 0, 40)
ZoomBtn.Position = UDim2.new(0.05, 0, 0.62, 0)
ZoomBtn.BackgroundColor3 = Color3.fromRGB(46, 204, 113)
ZoomBtn.TextColor3 = Color3.new(1, 1, 1)
ZoomBtn.Font = Enum.Font.FredokaOne
ZoomBtn.Parent = MainFrame
Instance.new("UICorner", ZoomBtn)

ZoomBtn.MouseButton1Click:Connect(function()
    player.CameraMaxZoomDistance = 10000
    ZoomBtn.Text = "✅ DONE"
    task.wait(1)
    ZoomBtn.Text = "🔓 UNLOCK ZOOM"
end)

local CloseBtn = Instance.new("TextButton")
CloseBtn.Text = "إغلاق"
CloseBtn.Size = UDim2.new(0.9, 0, 0, 35)
CloseBtn.Position = UDim2.new(0.05, 0, 0.82, 0)
CloseBtn.BackgroundColor3 = Color3.fromRGB(192, 57, 43)
CloseBtn.TextColor3 = Color3.new(1, 1, 1)
CloseBtn.Font = Enum.Font.FredokaOne
CloseBtn.Parent = MainFrame
Instance.new("UICorner", CloseBtn)

CloseBtn.MouseButton1Click:Connect(function() ScreenGui:Destroy() end)

-- تشغيل الكشف التلقائي فوراً عند فتح السكربت
autoDetectLocation()

-- إعادة الكشف عند الموت أو العودة للماب
player.CharacterAdded:Connect(function()
    task.wait(1)
    autoDetectLocation()
end)