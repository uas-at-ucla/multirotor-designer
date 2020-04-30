% John Tabakian
% UAS@UCLA 2019-2020
% First Responder Competition
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% NOTES:
% Does not account for battery voltage yet. Assumes all batteries are 6S

clear all; close all; clc;

%% Input Parameters
global alt I g m_payload m_airframe m_arm
alt = 300; %Flight altitude relative to LZ [m]
I = linspace(0, 47.73, 10000); %[Amps]
g = 9.81; %Gravitational acceleration [m * s^-2]
m_payload = 4.53592; %Mass of NIST Payload [kg]
m_airframe = 4.53592; %Mass of airframe excluding arms & batteries [kg]
m_arm = .598; %Mass of individual arm [kg]
max_batteries = 10;

%% Load Motors
[status,sheets] = xlsfinfo('Motors.xlsx');
Motors = zeros(length(sheets), 8);
for i = 1:1:length(sheets)
    Motors(i, 1:3) = readmatrix('Motors.xlsx',...
                                'Sheet', i, 'Range','A2:C2');
    Motors(i, 4:6) = transpose(readmatrix('Motors.xlsx',...
                                'Sheet', i, 'Range','F26:F28'));
    Motors(i, 7:8) = transpose(readmatrix('Motors.xlsx',...
                                'Sheet', i, 'Range','G26:G27'));
end

%% Load Generators
[status,sheets] = xlsfinfo('Generators.xlsx');
Generators = zeros(length(sheets), 6);
for i = 1:1:length(sheets)
    Generators(i, 1:6) = readmatrix('Generators.xlsx',...
                                'Sheet', i, 'Range','A2:F2');
end

%% Load Batteries
[status,sheets] = xlsfinfo('Batteries.xlsx');
Batteries = zeros(length(sheets), 4);
for i = 1:1:length(sheets)
    Batteries(i, 1:4) = readmatrix('Batteries.xlsx',...
                                'Sheet', i, 'Range','A2:D2');
end

%% Iteration
max_t = -1;
max_t_config = -1*ones(1,6);
max_eff = -1;
max_eff_config = -1*ones(1,6);
for generator = 1:1:length(Generators(:,1))
    for motor = 1:1:length(Motors(:,1))
        for battery = 1:1:length(Batteries(:,1))
            for n_motor = 4:1:12
                for n_bat_parallel = 1:1:max_batteries/2
                    for fuel = 0.1:0.05:5
                        [time, throttle, efficiency] ...
                            = flight(n_motor, Motors(motor,:), n_bat_parallel,...
                                Batteries(battery,:), fuel, Generators(generator,:));
                        if efficiency > max_eff
                            max_eff = efficiency;
                            max_eff_config = [motor, n_motor, battery, n_bat_parallel, fuel, generator];
                        end
                        if time > max_t
                            max_t = time;
                            max_t_config = [motor, n_motor, battery, n_bat_parallel, fuel, generator];
                        end
                    end
                end
            end    
        end
    end
end
clc;
fprintf(['max_eff_config: Motor ' num2str(max_eff_config(1))...
        ', Battery ' num2str(max_eff_config(3))...         
        ', Generator ' num2str(max_eff_config(6))...
         ', ' num2str(max_eff_config(2)) ' motors, '... 
              num2str(max_eff_config(4)*2) ' batteries, '...
              num2str(max_eff_config(5)) ' L \n']);
fprintf(['max_t_config: Motor ' num2str(max_t_config(1))...
         ', Battery ' num2str(max_eff_config(3))...
         ', Generator ' num2str(max_t_config(6))...
         ', ' num2str(max_t_config(2)) ' motors, '... 
              num2str(max_t_config(4)*2) ' batteries, '...
              num2str(max_t_config(5)) ' L \n']);
fprintf(['========================================='...
        '=========================================\n']);

%% User Input
while true
    motor = input('(CTRL+C TO STOP)\nMotor Sheet #: ');
    if motor > length(Motors(:,1))
        continue
    end
    battery = input('Battery Sheet #: ');
    if battery > length(Batteries(:,1))
        continue
    end
    generator = input('Generator Sheet #: ');
    if generator > length(Generators(:,1))
        continue
    end
    n_motor = input('Number of Motors (>2): ');
    n_bat = input('Total Number of Batteries (>2): ');
    fuel = input('Fuel Capacity [L]: ');
    if (fuel >= 0)
        [time, throttle, efficiency] = flight(n_motor, Motors(motor,:),...
            n_bat/2, Batteries(battery,:), fuel, Generators(generator,:));
    else
        [time, throttle, efficiency] = flight(n_motor, Motors(motor,:),...
            n_bat/2, Batteries(battery,:), 0, zeros(1,6));
    end
    fprintf(['Flight Time [min]: ' num2str(time)...
        ' , Throttle: ' num2str(throttle*100)...
        '%%, Motor Efficiency [g/W]: ' num2str(efficiency) '\n']);
    fprintf(['========================================='...
        '=========================================\n']);
end
            
%% Functions
function val = m(n_motor, mspecs, n_battery, bspecs, fuel, gspecs)
    global m_payload m_airframe m_arm
    val = m_payload + m_airframe...
        + n_motor*(m_arm + mspecs(1,1)...
        + mspecs (1,2))+ n_battery*bspecs...
        + fuel*gspecs(3)/1000 + gspecs(1);
end
function [time, throttle, efficiency] = flight(n_motor, mspecs, n_bat_parallel, bspecs, fuel, gspecs)
    global alt g
    n_bat = 2*n_bat_parallel;
    mass = m(n_motor, mspecs(1,1:2), n_bat, bspecs(1,1), fuel, gspecs)
    T = (1/n_motor)*(1+g)*mass %T_Flight [N] (for hover change from 1+g to g)
    currentDraw = n_motor*(mspecs(1,4))...
        *(T*1000/(g))^mspecs(1,5) %Total Current Draw [A]
    if currentDraw > n_motor*mspecs(1,6)...
            || currentDraw > 1000*gspecs(6)/gspecs(5)...
            || currentDraw > bspecs(1,3)*bspecs(1,4)
        time = -1;
        throttle = -1;
        efficiency = -1;
        return
    end
    %timeToAlt = sqrt(2*alt/...
        %((mspecs(1,6)/mspecs(1,4))^(1/mspecs(1,5))*g/(1000*mass))) %[s]
    ampH = n_bat_parallel*bspecs(3)... %Amp-Hours left after Takeoff
            %-mspecs(1,6)*timeToAlt/(60^2)
    Battery_Time = (60)*ampH/currentDraw %[m]
    Gas_Time = fuel*60/gspecs(4) %[min]
    if isnan(Gas_Time)
        time = Battery_Time; %[min]
    else
        time = Battery_Time + Gas_Time; %Total Flight Time [min]
    end
    throttle = mspecs(1,7)*(currentDraw/n_motor)^mspecs(1,8); %
    efficiency = T*1000/...
        (g*bspecs(2)*2*currentDraw/n_motor); %[g/W]
end

