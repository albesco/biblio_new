clear
close all
clc
%%
h_time=1980:2024;


%%
x=fileread('All.csv');
% x=fileread('Castellini.csv');

x = strrep(x,'''DOI not found or an error occurred.''','0');
x = strrep(x,'None','0');
x = strrep(x,'"','');


a=ismember(x, char([10 13]));
ind=find(a==1);

jj=0;
for ii=1:length(ind)-1
    r=x(ind(ii):ind(ii+1));
    if(rem(ii,2) == 0)
        jj=jj+1;

        q=strfind(r,',');

        author(jj,:)=str2num(r(q(3)+1:q(4)-1));
        w=r(q(4)+1:q(5)-1);
        qq=strfind(w,'-');
        eid(jj)=str2num(w(qq(end)+1:end));

        article_year(jj)=str2num(r(q(5)+1:q(6)-1));
        num_aut(jj)=str2num(r(q(6)+1:q(7)-1));
        num_cit(jj)=str2num(r(q(7)+1:q(8)-1));
        article_refs(jj)=str2num(r(q(8)+1:q(9)-1));
        num_ref_in_citing(jj)=str2num(r(q(9)+1:q(10)-1));
        p1=strfind(r,'[')+1;
        p2=strfind(r,']')-1;
        y=r(p1:p2);
        e=strfind(y,',');
        yea=[];
        if(length(e)>1)
            yea(1)=str2num(y(1:e(1)-1));
            for kk=2:length(e)
                yea(kk)=str2num(y(e(kk-1):e(kk)));
            end
        end
        years{jj}=yea;   
    end
end
clear y yea
years=years';

for jj=1:length(years)
    x=years{jj};
    if(length(x)>0)
        m=floor(mean(x(x~=0)));
        id=find(x==0);
        x(id)=m;
        years{jj}=x;
    end
end

aut_list=unique(author);

clear a e id ind m p1 p2 q r x kk ii jj w qq
%% Elaborazione
figure, plot(article_year,num_aut,'*')

%% Eliminazione articoli ripetuti
[article_unique,ia,ic] = unique(eid);

art_refs_unique=article_refs(ia);
art_year_unique=article_year(ia);
num_aut_unique=num_aut(ia);
num_cit_unique=num_cit(ia);
num_ref_cit_unique=num_ref_in_citing(ia);
years_unique=years(ia);
%% Numeo autori medio per ogni anno
for ii=1:length(h_time)
    ind=find(art_year_unique==h_time(ii));
    A=num_aut_unique(ind);
    B = rmoutliers(A);
    num_aut_ave(ii)=mean(B);
    num_aut_std(ii)=std(B);
end
figure, plot(h_time,num_aut_ave), hold on
plot(h_time,num_aut_ave+num_aut_std)
plot(h_time,num_aut_ave-num_aut_std)
xlabel('Publication Year')
ylabel('Number of Authors Average')
title('Average author number per year')
hold on


%% Numero references medio per anno
for ii=1:length(h_time)
    ind=find(art_year_unique==h_time(ii));
    A=art_refs_unique(ind);
    B = rmoutliers(A);
    num_ref_ave(ii)=mean(B);
    num_ref_std(ii)=std(B);
end
figure, plot(h_time,num_ref_ave), hold on
plot(h_time,num_ref_ave+num_ref_std)
plot(h_time,num_ref_ave-num_ref_std)
xlabel('Publication Year')
ylabel('Number of Citations Average')
title('Average References number per year')
hold on



%% H-index e C-index

% Initialize variables
% h_authors = [];
% cit_authors = [];
% C_authors = [];
% cit_authors_weight = [];

for ii = 1:length(aut_list)    
    ind=find(author==aut_list(ii));

    num_cit_vector=num_cit(ind);
    % H-index calculation
    num_cit_vector = sort(num_cit_vector, 'descend');
    h_index = 0;
    n_cit = 0;
    for jj = 1:length(num_cit_vector)
        n = num_cit_vector(jj);
        n_cit = n_cit + n;
        if n >= jj
            h_index = h_index + 1;
        end
    end
    h_authors(ii) = h_index;
    cit_authors(ii) = n_cit;
    
    % C-index calculation
    num_cit_v_weight = num_ref_in_citing(ind);
    num_cit_v_weight = sort(num_cit_v_weight, 'descend');
    C_index = 0;
    C_cit = 0;
    for jj = 1:length(num_cit_v_weight)
        n = num_cit_v_weight(jj);
        C_cit = C_cit + n;
        if 10*n >= jj   % !!!!!!!!!!!!!!!!!!!!!!!!!  10???  !!!!!!!!!!!!!!!!!!!!!!!!
            C_index = C_index + 1;
        end
    end
    C_authors(ii) = C_index;
    cit_authors_weight(ii) = C_cit;
end


%% Calcolo dell'andamento di H-index nel tempo

for ii = 1:length(aut_list)    
    % ind=find(author==aut_list(ii));
    % 
    % num_cit_vector=num_cit_unique(ind);
    % a_y=article_year(ind);

    for kk=1:length(h_time)
        id=find((article_year<=h_time(kk))' & author==aut_list(ii));
        num_cit_vector=num_cit(id);
        a_y=article_year(id);

        % H-index calculation
        num_cit_vector = sort(num_cit_vector, 'descend');
        h_index = 0;
        n_cit = 0;
        for jj = 1:length(num_cit_vector)
            n = num_cit_vector(jj);
            n_cit = n_cit + n;
            if n >= jj
                h_index = h_index + 1;
            end
        end
        h_authors_y(ii,kk) = h_index;
        cit_authors_y(ii,kk) = n_cit;
    
    % C-index calculation
        num_cit_v_weight = num_ref_in_citing(id);
        num_cit_v_weight = sort(num_cit_v_weight, 'descend');
        C_index = 0;
        C_cit = 0;
        for jj = 1:length(num_cit_v_weight)
            n = num_cit_v_weight(jj);
            C_cit = C_cit + n;
            if 10*n >= jj   % !!!!!!!!!!!!!!!!!!!!!!!!!  10???  !!!!!!!!!!!!!!!!!!!!!!!!
                C_index = C_index + 1;
            end
        end
        C_authors_y(ii,kk) = C_index;
        cit_authors_weight_y(ii,kk) = C_cit;
    end
end

figure, plot(h_time,h_authors_y,'-*')
%% H-index slope

for ii = 1:length(aut_list)
    ind=find(h_authors_y(ii,:)>0);
    y_start(ii)=h_time((min(ind)-1));
    t=h_time((min(ind)-1):end);
    y=h_authors_y(ii,(min(ind)-1):end);
    [fitresult, gof] = createFit(t, y);
    h_slope(ii)=fitresult.p1;
end

figure, plot(y_start,h_slope,'*'), hold on
fitres=createFit1(y_start,h_slope);
plot(fitres)
hold off