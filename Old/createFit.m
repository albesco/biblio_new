function [fitresult, gof] = createFit(t, y)


%% Fit: 'untitled fit 1'.
[xData, yData] = prepareCurveData( t, y );

% Set up fittype and options.
ft = fittype( 'poly1' );

% Fit model to data.
[fitresult, gof] = fit( xData, yData, ft );

% % Plot fit with data.
% figure( 'Name', 'untitled fit 1' );
% h = plot( fitresult, xData, yData );
% legend( h, 'y vs. t', 'untitled fit 1', 'Location', 'NorthEast', 'Interpreter', 'none' );
% % Label axes
% xlabel( 't', 'Interpreter', 'none' );
% ylabel( 'y', 'Interpreter', 'none' );
% grid on


