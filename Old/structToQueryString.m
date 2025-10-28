function queryString = structToQueryString(structure)
    % Converti una struttura in una stringa di query URL.
    fields = fieldnames(structure);
    values = struct2cell(structure);
    pairs = strcat(fields, '=', urlencode(values));
    queryString = strjoin(pairs, '&');
